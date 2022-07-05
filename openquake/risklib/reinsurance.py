# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2022, GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

import pandas as pd
import numpy as np


def reinsured_losses(exposure, losses, policy, treaty):
    '''
    Parameters
    ----------
    exposure : DataFrame
        Exposure in OQ format (asset_id, taxonomy, ...)
    losses : DataFrame
        Average annual losses per asset (asset_id, structural, ...)
    policy : DataFrame
        Description of policy characteristics in OQ format.
    treaty : DataFrame
        Description of reinsurance characteristics in OQ format.

    Returns
    -------

    Complete DataFrame with calculation details.
    '''

    # Input validation (to be implemented):
    # ------------------------------------------------------------------------
    #  EXPOSURE MODEL
    #   - Exposure model in OQ format and with 'policy' column
    #
    #  POLICY AND REINSURANCE FILES
    #   - Check that all policies in assets are within policy file
    #   - For the following colummns check:
    #       `policy`        : each row should be unique (no duplicated policy)
    #       `policy_unit`   : str. Options: ['asset', 'policy']
    #       `liability`     : float >= 0
    #       `deductible`    : float >= 0
    #       `min_deductible`: float >= 0
    #
    # POLICY AND REINSURANCE FILES
    #   - Check that all treaties in policies are within reinsurance file
    #   - For the following colummns check:
    #       `treaty`      : each row should be unique (no duplicated treaty)
    #       `treaty_type` : str.
    #           Options: ['quota_share', 'surplus', 'WXL', 'CatXL']
    #       `treaty_unit `: str.
    #           Options: ['policy', 'treaty', 'event']
    #       `qs_retention`:  0 <= float <= 1
    #       `qs_cession`  :  0 <= float <= 1
    #       `surplus_line`: float >= 0
    #       `treaty_limit`: float >= 0
    # Create single dataframe with total values (exposure and losses)
    assets = tot_cost_losses(exposure, losses)

    # Estimate absolute liability and deductible at policy_unit
    df = process_insurance(assets, policy)

    # Apply reinsurance treaties
    return compute_reinsurance(df, treaty)


def apply_treaty(row, n):
    '''
    Assign appropriate treaty to apply for each row in the DataFrame
    '''
    if row.treaty_unit in ['treaty', 'event']:
        # Pending to implement
        print('Need to adjust code. It is missing the implementation for',
              'treaty_units = `treaty` or `event`')

    if row.treaty_type == 'quota_share':
        row = quota_share(row)

    elif row.treaty_type == 'surplus':
        row = surplus(row)

    elif row.treaty_type != row.treaty_type:  # If treaty_type is NaN then ..
        if n == 0:
            # No reinsurance treaty. All losses go to retention
            row['retention'] = row.claim
            row['cession'] = 0
            row['remainder'] = 0
        else:
            row['retention'] = row[f'retention_{n}']
            row['cession'] = row[f'cession_{n}']
            row['remainder'] = row[f'remainder_{n}']

    else:
        assert f'Error. Not supported treaty_type {row.treaty_type}'

    return row


def quota_share(row):
    """
    In a quota share treaty, return the `retention`, `cession` and `remainder`.
    The function is applied per row (either asset, policy or treaty).
    A previous aggregation at the specified unit needs to be done in advance

    The "row" input must have the following attributes:

        deductible: max(deductible, min_deductible)
        liability: absolute value with respect to the treaty unit
        qs_retention: fraction (proportion)
        qs_cession: fraction (proportion)
        treaty_limit: absolute value with respect to the treaty unit
        claim: absolute value with respect to the treaty unit
    """

    claim = row.claim
    liability = row.liability
    qs_retention = row.qs_retention  # 0 <= float <= 1
    qs_cession = row.qs_cession      # 0 <= float <= 1
    treaty_limit = row.treaty_limit

    # Adjust qs proportions when liability > traty_limit
    if liability <= treaty_limit:
        retention = claim * qs_retention
        cession = claim * qs_cession
        remainder = 0
    else:
        retention = claim * qs_retention * treaty_limit / liability
        cession = claim * qs_cession * treaty_limit / liability
        remainder = claim * (liability - treaty_limit)/liability
    assert np.isclose(remainder, max(0, claim - retention - cession),
                      0.0001), 'Check remainder calcs'
    row['retention'] = retention
    row['cession'] = cession
    row['remainder'] = remainder

    return row


def surplus(row):
    """
    In a surplus treaty, return the `retention`, `cession` and `remainder`.
    The function is applied per row (either asset, policy or treaty).
    A previous aggregation at the specified unit needs to be done in advance
    The "row" input must have the following attributes:

        deductible: max(deductible, min_deductible)
        liability: absolute value with respect to the treaty unit
        line: maximum retention limit (integer, units)
        treaty_limit: absolute value with respect to the treaty unit.
                       = underwriting capacity
                       = retention + treaty_capacity (reinsurance allocation)
        claim: absolute value with respect to the treaty unit
    """

    claim = row.claim
    liability = row.liability
    line = row.surplus_line
    treaty_limit = row.treaty_limit

    # Adjust Surplus proportions when liability > traty_limit
    if liability <= line:
        retention = claim
        cession = 0
        remainder = 0

    elif liability <= treaty_limit:
        retention = claim * line / liability
        cession = claim * (liability - line) / liability
        remainder = 0

    else:
        retention = claim * line / liability
        cession = claim * (treaty_limit - line) / liability
        remainder = claim * (liability - treaty_limit)/liability

    assert np.isclose(remainder, max(0, claim - retention - cession),
                      0.0001), 'Check remainder calcs'

    row['retention'] = retention
    row['cession'] = cession
    row['remainder'] = remainder

    return row


def tot_cost_losses(exposure, losses):
    """
    Estimate total exposed value and total loss considering all loss types
        (str + nonstr + contents)

    !!! NOTE: If the exposure is specified per area or per building
        (as opposed to total cost), then it is necessary to estimate total cost

    Returns
    -------
    assets:
        DataFrame with total exposure and losses
    """
    exposure['total_cost'] = exposure.structural
    # + exposure.nonstructural + exposure.contents
    losses['losses'] = losses.structural
    # + losses.nonstructural + losses.contents
    assets = exposure.merge(losses[['asset_id', 'losses']],
                            how='left',
                            on='asset_id').fillna(0)
    assert assets.losses.sum() != 0, 'No losses in exposure model'

    return assets


def process_insurance(assets, df_policy):
    """
    Estimate effective values for the specified "policy_units"
    """

    # Create policy dataframe where all values are applicable per "policy_unit"
    cols = ['asset_id', 'policy', 'total_cost', 'losses']

    # -  for policies at "asset" level:
    p_asset = df_policy.policy[df_policy.policy_unit == 'asset']
    df_a = assets[cols][assets.policy.isin(p_asset)]

    # -  for policies at "policy" level:
    p_policy = df_policy.policy[df_policy.policy_unit == 'policy']
    df_p = assets[cols][assets.policy.isin(p_policy)]
    df_p = df_p.groupby(by='policy').sum().reset_index()

    # merge values
    df = pd.concat([df_a, df_p])
    df = df.merge(df_policy, on='policy')
    assert df.empty is False, 'Empty DataFrame. Check input files'

    # Estimate absolute values from fractions at the "policy_units" level
    # When values <= 1, then assume input is a fraction
    df.loc[df.liability <= 1, 'liability'] = df.liability * df.total_cost
    df.loc[df.deductible <= 1, 'deductible'] = df.deductible * df.total_cost

    # Effective deductible
    df.deductible = df[['deductible', 'min_deductible']].max(axis=1)
    df.deductible.fillna(0, inplace=True)
    df.drop(columns={'min_deductible'}, inplace=True)

    # When losses > liability, only cover up to the liability value
    # Include column for no_insured losses when applicable
    no_insured = df['losses'] - df['liability']
    no_insured[no_insured <= 0] = 0  # Minimum no_insured = 0
    if any(no_insured > 0):
        df['no_insured'] = no_insured

    # Estimate claim
    df['claim'] = df.losses - df.deductible
    df.loc[df['claim'] < 0, 'claim'] = 0  # Minimum claim = 0

    # Maximum claim up to liability
    mask = df['claim'] > df['liability']
    df.loc[mask, 'claim'] = df.loc[mask, 'liability']

    return df


def compute_reinsurance(data, reinsurance):
    """
    Returns a DataFrame with the losses for the reinsurance company
    """
    # Identify layers of treaties applicable for each policy
    data['layers'] = data.treaty.str.split(',')
    mask = ~data.treaty.isna()
    data['n_layers'] = data[mask].treaty.str.split(',').apply(len)

    # Estimate reinsurance values for first layer
    print('  estimating reinsurance layer 1')
    df = data.copy()
    df['treaty'] = data.treaty.str.split(',', expand=True)[0].str.strip()
    df_ins = df.merge(reinsurance, on='treaty', how='left')
    df_ins = df_ins.apply(apply_treaty, args=[0], axis=1).apply(pd.Series)

    # MULTIPLE REINSURANCE LEVELS

    # Validation
    # ----------
    # 1. UPPER layer retention limit == treaty_limit UNDERLYING layer

    cols = ['asset_id', 'policy', 'retention', 'cession', 'remainder']
    max_layers = data.n_layers.max().astype(int)
    if max_layers >= 2:
        for n in range(1, max_layers):
            print(f'  estimating reinsurance layer {n + 1}')

            # Get previous layer estimates
            layer_n = df_ins.loc[:, cols]
            layer_n.rename(columns={'retention': f'retention_{n}',
                                    'cession': f'cession_{n}',
                                    'remainder': f'remainder_{n}'},
                           inplace=True)
            df = df.merge(layer_n, how='left')  # raise errors if empty

            # Currently only SURPLUS upper layers are supported
            # The upper layer reinsurance is applied to the remainder
            df_ins = df.copy()
            df_ins['treaty'] = data.treaty.str.split(',', expand=True)[
                n].str.strip()
            df_ins = df_ins.merge(reinsurance, on='treaty', how='left')
            assert df_ins['treaty_type'].isin(['surplus', np.nan]).all(), \
                'Check upper layers treaty_type. Only Surplus is supported'
            df_ins = df_ins.apply(apply_treaty, args=[n], axis=1).apply(
                pd.Series)

        # Rename last layer
        layer_n = df_ins.loc[:, cols]
        layer_n.rename(columns={'retention': f'retention_{n + 1}',
                                'cession': f'cession_{n + 1}',
                                'remainder': f'remainder_{n + 1}'},
                       inplace=True)
        df = df.merge(layer_n, how='left')  # raise errors if empty

        # Add deductible in reinsurance input
        df['treaty'] = data['treaty']
        df['retention'] = df['retention_1']
        df['cession'] = df['claim'] - df['retention'] - df[
            f'remainder_{n + 1}']
        df['remainder'] = df[f'remainder_{n+1}']
    else:
        df = df_ins

    return df
