Classical PSHA that utilises Christchurch-specific gsims and GMtoLHC horizontal component conversion
====================================================================================================

+----------------+----------------------+
| checksum32     | 2_329_454_136        |
+----------------+----------------------+
| date           | 2022-03-17T11:24:26  |
+----------------+----------------------+
| engine_version | 3.14.0-gitaed816bf7b |
+----------------+----------------------+
| input_size     | 3_762                |
+----------------+----------------------+

num_sites = 2, num_levels = 4, num_rlzs = 1

Parameters
----------
+---------------------------------+--------------------------------------------+
| parameter                       | value                                      |
+---------------------------------+--------------------------------------------+
| calculation_mode                | 'preclassical'                             |
+---------------------------------+--------------------------------------------+
| number_of_logic_tree_samples    | 0                                          |
+---------------------------------+--------------------------------------------+
| maximum_distance                | {'default': [[2.5, 200.0], [10.2, 200.0]]} |
+---------------------------------+--------------------------------------------+
| investigation_time              | 50.0                                       |
+---------------------------------+--------------------------------------------+
| ses_per_logic_tree_path         | 1                                          |
+---------------------------------+--------------------------------------------+
| truncation_level                | 3.0                                        |
+---------------------------------+--------------------------------------------+
| rupture_mesh_spacing            | 5.0                                        |
+---------------------------------+--------------------------------------------+
| complex_fault_mesh_spacing      | 5.0                                        |
+---------------------------------+--------------------------------------------+
| width_of_mfd_bin                | 0.1                                        |
+---------------------------------+--------------------------------------------+
| area_source_discretization      | None                                       |
+---------------------------------+--------------------------------------------+
| pointsource_distance            | {'default': '1000'}                        |
+---------------------------------+--------------------------------------------+
| ground_motion_correlation_model | None                                       |
+---------------------------------+--------------------------------------------+
| minimum_intensity               | {}                                         |
+---------------------------------+--------------------------------------------+
| random_seed                     | 20                                         |
+---------------------------------+--------------------------------------------+
| master_seed                     | 123456789                                  |
+---------------------------------+--------------------------------------------+
| ses_seed                        | 42                                         |
+---------------------------------+--------------------------------------------+

Input files
-----------
+-------------------------+--------------------------------------------------------------+
| Name                    | File                                                         |
+-------------------------+--------------------------------------------------------------+
| amplification           | `amplification.csv <amplification.csv>`_                     |
+-------------------------+--------------------------------------------------------------+
| gsim_logic_tree         | `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                 |
+-------------------------+--------------------------------------------------------------+
| job_ini                 | `job.ini <job.ini>`_                                         |
+-------------------------+--------------------------------------------------------------+
| site_model              | `site_model.xml <site_model.xml>`_                           |
+-------------------------+--------------------------------------------------------------+
| source_model_logic_tree | `source_model_logic_tree.xml <source_model_logic_tree.xml>`_ |
+-------------------------+--------------------------------------------------------------+

Required parameters per tectonic region type
--------------------------------------------
+----------------------+---------------------+-----------+------------+------------+
| trt_smr              | gsims               | distances | siteparams | ruptparams |
+----------------------+---------------------+-----------+------------+------------+
| Active Shallow Crust | [BooreAtkinson2008] | rjb       | vs30       | mag rake   |
+----------------------+---------------------+-----------+------------+------------+

Slowest sources
---------------
+-----------+------+-----------+-----------+--------------+
| source_id | code | calc_time | num_sites | eff_ruptures |
+-----------+------+-----------+-----------+--------------+
| 1         | X    | 0.0       | 2         | 1            |
+-----------+------+-----------+-----------+--------------+

Computation times by source typology
------------------------------------
+------+-----------+-----------+--------------+---------+
| code | calc_time | num_sites | eff_ruptures | weight  |
+------+-----------+-----------+--------------+---------+
| X    | 0.0       | 2         | 1            | 2.02000 |
+------+-----------+-----------+--------------+---------+

Information about the tasks
---------------------------
+--------------------+--------+---------+--------+-----------+---------+---------+
| operation-duration | counts | mean    | stddev | min       | max     | slowfac |
+--------------------+--------+---------+--------+-----------+---------+---------+
| preclassical       | 2      | 0.00182 | 88%    | 2.038E-04 | 0.00344 | 1.88812 |
+--------------------+--------+---------+--------+-----------+---------+---------+
| read_source_model  | 1      | 0.02490 | nan    | 0.02490   | 0.02490 | 1.00000 |
+--------------------+--------+---------+--------+-----------+---------+---------+

Data transfer
-------------
+-------------------+------------------------------------------+----------+
| task              | sent                                     | received |
+-------------------+------------------------------------------+----------+
| read_source_model |                                          | 3.29 KB  |
+-------------------+------------------------------------------+----------+
| split_task        | args=1.02 MB elements=2.97 KB func=132 B | 0 B      |
+-------------------+------------------------------------------+----------+
| preclassical      |                                          | 4.47 KB  |
+-------------------+------------------------------------------+----------+

Slowest operations
------------------
+---------------------------+-----------+-----------+--------+
| calc_50540, maxmem=1.9 GB | time_sec  | memory_mb | counts |
+---------------------------+-----------+-----------+--------+
| importing inputs          | 0.15789   | 0.0       | 1      |
+---------------------------+-----------+-----------+--------+
| composite source model    | 0.13799   | 0.0       | 1      |
+---------------------------+-----------+-----------+--------+
| total read_source_model   | 0.02490   | 0.0       | 1      |
+---------------------------+-----------+-----------+--------+
| total preclassical        | 0.00344   | 0.54688   | 1      |
+---------------------------+-----------+-----------+--------+
| weighting sources         | 0.00256   | 0.0       | 1      |
+---------------------------+-----------+-----------+--------+
| splitting sources         | 3.443E-04 | 0.0       | 1      |
+---------------------------+-----------+-----------+--------+