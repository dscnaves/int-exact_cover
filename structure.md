# Project Structure

int-exact_cover
├─ README.md
├─ bin
│  └─ processar_grafo
├─ docs
├─ instances
│  ├─ CiscoSecureWorkload_22_networks
│  └─ my_testes
│     ├─ Instances - Optimizing INT.xlsx
│     ├─ cisco.txt
│     └─ teste_dani.txt
├─ results
│  ├─ C_parsed_data
│  │  └─ teste_dani_parsed.txt
│  ├─ gurobi
│  │  └─ py_parsed_data_gurobi_result.txt
│  ├─ plots
│  │  └─ graph.png
│  └─ py_parsed_data
│     ├─ E_for_gurobi.pkl
│     ├─ S_for_gurobi.pkl
│     ├─ edges.csv
│     ├─ paths_by_group.json
│     ├─ teste_dani_c_data.txt
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
│  │  │  ├─ heuristic_3.c
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
│     ├─ draw_graph_from_csv.py
│     ├─ exporters.py
│     ├─ file_parser.py
│     ├─ graph_structs.py
│     ├─ main_parse_edges.py
│     ├─ path_reconstruction.py
│     └─ processar_grafo.c
└─ structure.md
