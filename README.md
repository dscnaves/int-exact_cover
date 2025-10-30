# Exact Coverage of In-band Networks Telemetry
This repository contains the implementation and experiments related to my undergraduate research problem, which approach the Exact Coverage of In-band Networks Telemetry in an efficient and heuristic way.

## Project Structure

```
int-exact_cover
├─ README.md
├─ bin
│  └─ processar_grafo
├─ docs
│  ├─ papers
│  │  ├─ 1 (2024) Optimizing in-band network telemetry problem.pdf
│  │  ├─ 2 (2019) An optimization-based approach for efficient network monitoring using in-band network telemetry.pdf
│  │  ├─ 3 (2023) Scheduling In-Band Network Telemetry with Convergence-Preserving Federated Learning.pdf
│  │  ├─ 4 (2023) On_Orchestration_of_Segment_Routing_and_In-Band_Network_Telemetry.pdf
│  │  └─ notes
│  └─ reports
│     ├─ Formulação do Problema.pdf
│     ├─ Relatório Técnico Parcial.pdf
│     └─ pind___bolsa_1.pdf
├─ instances
│  ├─ CiscoSecureWorkload_22_networks
│  │  └─ Cisco_22_networks
│  │     ├─ README
│  │     ├─ dir_20_graphs
│  │     │  ├─ dir_day1
│  │     │  │  ├─ out1_1.txt
│  │     │  │  ├─ out1_1.txt.gz
│  │     │  │  ├─ out1_2.txt.gz
│  │     │  │  ├─ out1_3.txt.gz
│  │     │  │  ├─ out1_4.txt.gz
│  │     │  │  ├─ out1_5.txt.gz
│  │     │  │  └─ out1_6.txt.gz
│  │     │  ├─ dir_day2
│  │     │  │  ├─ out2_1.txt.gz
│  │     │  │  ├─ out2_2.txt
│  │     │  │  ├─ out2_2.txt.gz
│  │     │  │  ├─ out2_3.txt.gz
│  │     │  │  ├─ out2_4.txt.gz
│  │     │  │  ├─ out2_5.txt.gz
│  │     │  │  ├─ out2_6.txt.gz
│  │     │  │  └─ out2_7.txt.gz
│  │     │  ├─ dir_day3
│  │     │  │  ├─ out3_1.txt.gz
│  │     │  │  ├─ out3_2.txt.gz
│  │     │  │  ├─ out3_3.txt.gz
│  │     │  │  ├─ out3_4.txt.gz
│  │     │  │  ├─ out3_5.txt.gz
│  │     │  │  ├─ out3_6.txt.gz
│  │     │  │  └─ out3_7.txt.gz
│  │     │  └─ dir_day4
│  │     │     ├─ out4_1.txt.gz
│  │     │     ├─ out4_2.txt.gz
│  │     │     ├─ out4_3.txt.gz
│  │     │     ├─ out4_4.txt.gz
│  │     │     ├─ out4_5.txt.gz
│  │     │     ├─ out4_6.txt.gz
│  │     │     └─ out4_7.txt.gz
│  │     ├─ dir_g21_small_workload_with_gt
│  │     │  ├─ dir_includes_packets_and_other_nodes
│  │     │  │  ├─ edges_to_ports_202202100000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202100900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202101900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202102000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202102100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202102200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202102300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202110900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202111900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202112000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202112100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202112200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202112300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202120900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202121900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202122000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202122100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202122200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202122300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202130900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131200.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131300.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131400.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131500.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131600.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131700.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131800.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202131900.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202132000.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202132100.anon.txt.gz
│  │     │  │  ├─ edges_to_ports_202202132200.anon.txt.gz
│  │     │  │  └─ edges_to_ports_202202132300.anon.txt.gz
│  │     │  ├─ dir_no_packets_etc
│  │     │  │  ├─ dir_few_sensors
│  │     │  │  │  ├─ README
│  │     │  │  │  ├─ edges_1days_tillFeb9_partial_sensors.csv.txt.gz
│  │     │  │  │  └─ edges_6days_tillFeb9_partial_sensors.csv.txt.gz
│  │     │  │  ├─ edges_12hrs_feb10_all_49sensors.csv.txt.gz
│  │     │  │  ├─ edges_2days_feb10thruFeb11_all_49sensors.csv.txt.gz
│  │     │  │  └─ edges_4days_feb10thruFeb13_all_49sensors.csv.txt.gz
│  │     │  ├─ groupings.gt.txt
│  │     │  ├─ groupings.gt.viaPrefix5.txt
│  │     │  └─ prefix_codes.txt
│  │     ├─ dir_g22_extra_graph_with_gt
│  │     │  ├─ candidate_gt.minPrefix5.txt
│  │     │  ├─ dir_edges
│  │     │  │  ├─ out2021_1_1.txt.gz
│  │     │  │  ├─ out2021_1_2.txt.gz
│  │     │  │  ├─ out2021_1_3.txt.gz
│  │     │  │  ├─ out2021_1_4.txt.gz
│  │     │  │  ├─ out2021_1_5.txt.gz
│  │     │  │  ├─ out2021_1_6.txt.gz
│  │     │  │  ├─ out2021_1_7.txt.gz
│  │     │  │  ├─ out2021_2_1.txt.gz
│  │     │  │  ├─ out2021_2_2.txt.gz
│  │     │  │  ├─ out2021_2_3.txt.gz
│  │     │  │  ├─ out2021_2_4.txt.gz
│  │     │  │  ├─ out2021_2_5.txt.gz
│  │     │  │  ├─ out2021_2_6.txt.gz
│  │     │  │  ├─ out2021_3_1.txt.gz
│  │     │  │  ├─ out2021_3_2.txt.gz
│  │     │  │  ├─ out2021_3_3.txt.gz
│  │     │  │  ├─ out2021_3_4.txt.gz
│  │     │  │  ├─ out2021_3_5.txt.gz
│  │     │  │  ├─ out2021_3_6.txt.gz
│  │     │  │  ├─ out2021_3_7.txt.gz
│  │     │  │  ├─ out2021_4_1.txt.gz
│  │     │  │  ├─ out2021_4_2.txt.gz
│  │     │  │  ├─ out2021_4_3.txt.gz
│  │     │  │  ├─ out2021_4_4.txt.gz
│  │     │  │  ├─ out2021_4_5.txt.gz
│  │     │  │  ├─ out2021_4_6.txt.gz
│  │     │  │  ├─ out2021_4_7.txt.gz
│  │     │  │  ├─ out2021_5_1.txt.gz
│  │     │  │  ├─ out2021_5_2.txt.gz
│  │     │  │  ├─ out2021_5_3.txt.gz
│  │     │  │  ├─ out2021_5_4.txt.gz
│  │     │  │  ├─ out2021_5_5.txt.gz
│  │     │  │  ├─ out2021_5_6.txt.gz
│  │     │  │  ├─ out2021_5_7.txt.gz
│  │     │  │  ├─ out2022_10_1.txt.gz
│  │     │  │  ├─ out2022_10_10.txt.gz
│  │     │  │  ├─ out2022_10_11.txt.gz
│  │     │  │  ├─ out2022_10_12.txt.gz
│  │     │  │  ├─ out2022_10_13.txt.gz
│  │     │  │  ├─ out2022_10_2.txt.gz
│  │     │  │  ├─ out2022_10_3.txt.gz
│  │     │  │  ├─ out2022_10_4.txt.gz
│  │     │  │  ├─ out2022_10_5.txt.gz
│  │     │  │  ├─ out2022_10_6.txt.gz
│  │     │  │  ├─ out2022_10_7.txt.gz
│  │     │  │  ├─ out2022_10_8.txt.gz
│  │     │  │  ├─ out2022_10_9.txt.gz
│  │     │  │  ├─ out2022_6_1.txt.gz
│  │     │  │  ├─ out2022_6_10.txt.gz
│  │     │  │  ├─ out2022_6_11.txt.gz
│  │     │  │  ├─ out2022_6_12.txt.gz
│  │     │  │  ├─ out2022_6_13.txt.gz
│  │     │  │  ├─ out2022_6_2.txt.gz
│  │     │  │  ├─ out2022_6_3.txt.gz
│  │     │  │  ├─ out2022_6_4.txt.gz
│  │     │  │  ├─ out2022_6_5.txt.gz
│  │     │  │  ├─ out2022_6_6.txt.gz
│  │     │  │  ├─ out2022_6_7.txt.gz
│  │     │  │  ├─ out2022_6_8.txt.gz
│  │     │  │  ├─ out2022_6_9.txt.gz
│  │     │  │  ├─ out2022_7_1.txt.gz
│  │     │  │  ├─ out2022_7_10.txt.gz
│  │     │  │  ├─ out2022_7_11.txt.gz
│  │     │  │  ├─ out2022_7_12.txt.gz
│  │     │  │  ├─ out2022_7_13.txt.gz
│  │     │  │  ├─ out2022_7_2.txt.gz
│  │     │  │  ├─ out2022_7_3.txt.gz
│  │     │  │  ├─ out2022_7_4.txt.gz
│  │     │  │  ├─ out2022_7_5.txt.gz
│  │     │  │  ├─ out2022_7_6.txt.gz
│  │     │  │  ├─ out2022_7_7.txt.gz
│  │     │  │  ├─ out2022_7_8.txt.gz
│  │     │  │  ├─ out2022_7_9.txt.gz
│  │     │  │  ├─ out2022_8_1.txt.gz
│  │     │  │  ├─ out2022_8_10.txt.gz
│  │     │  │  ├─ out2022_8_11.txt.gz
│  │     │  │  ├─ out2022_8_12.txt.gz
│  │     │  │  ├─ out2022_8_13.txt.gz
│  │     │  │  ├─ out2022_8_2.txt.gz
│  │     │  │  ├─ out2022_8_3.txt.gz
│  │     │  │  ├─ out2022_8_4.txt.gz
│  │     │  │  ├─ out2022_8_5.txt.gz
│  │     │  │  ├─ out2022_8_6.txt.gz
│  │     │  │  ├─ out2022_8_7.txt.gz
│  │     │  │  ├─ out2022_8_8.txt.gz
│  │     │  │  ├─ out2022_8_9.txt.gz
│  │     │  │  ├─ out2022_9_1.txt.gz
│  │     │  │  ├─ out2022_9_10.txt.gz
│  │     │  │  ├─ out2022_9_11.txt.gz
│  │     │  │  ├─ out2022_9_12.txt.gz
│  │     │  │  ├─ out2022_9_13.txt.gz
│  │     │  │  ├─ out2022_9_2.txt.gz
│  │     │  │  ├─ out2022_9_3.txt.gz
│  │     │  │  ├─ out2022_9_4.txt.gz
│  │     │  │  ├─ out2022_9_5.txt.gz
│  │     │  │  ├─ out2022_9_6.txt.gz
│  │     │  │  ├─ out2022_9_7.txt.gz
│  │     │  │  ├─ out2022_9_8.txt.gz
│  │     │  │  └─ out2022_9_9.txt.gz
│  │     │  └─ id_gt_path_code.txt
│  │     ├─ read_graphs.py
│  │     └─ read_gt.py
│  └─ my_testes
│     ├─ Instances - Optimizing INT.xlsx
│     ├─ cisco.txt
│     └─ teste_dani.txt
├─ results
│  ├─ C_parsed_data
│  │  └─ teste_dani_parsed.txt
│  ├─ gurobi
│  │  └─ py_parsed_data_gurobi_result.txt
│  └─ py_parsed_data
│     ├─ E_for_gurobi.pkl
│     ├─ S_for_gurobi.pkl
│     ├─ edges.csv
│     ├─ paths_by_group.json
│     ├─ teste_dani_parsed.txt
│     └─ vertices.csv
├─ src
│  ├─ __init__.py
│  ├─ __pycache__
│  │  └─ __init__.cpython-312.pyc
│  ├─ solver
│  │  ├─ draw_graph.py
│  │  ├─ heuristics
│  │  │  ├─ firsth_heuristic.py
│  │  │  ├─ v1_primeira_heurística.py
│  │  │  └─ v2_primeira_heurística.py
│  │  └─ rodar_modelo.py
│  └─ utils
│     ├─ __init__.py
│     ├─ __pycache__
│     │  ├─ __init__.cpython-312.pyc
│     │  ├─ exporters.cpython-312.pyc
│     │  ├─ file_parser.cpython-312.pyc
│     │  ├─ graph_structs.cpython-312.pyc
│     │  ├─ main.cpython-312.pyc
│     │  ├─ main_parse_edges.cpython-312.pyc
│     │  └─ path_reconstruction.cpython-312.pyc
│     ├─ exporters.py
│     ├─ file_parser.py
│     ├─ graph_structs.py
│     ├─ main_parse_edges.py
│     ├─ path_reconstruction.py
│     └─ processar_grafo.c
└─ structure.md

```