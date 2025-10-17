# Project Structure

int-exact_cover
├── bin
│   └── processar_grafo
├── docs
│   ├── papers
│   │   ├── notes
│   │   ├── 1 (2024) Optimizing in-band network telemetry problem.pdf
│   │   ├── 2 (2019) An optimization-based approach for efficient network monitoring using in-band network telemetry.pdf
│   │   └── 3 (2023) Scheduling In-Band Network Telemetry with Convergence-Preserving Federated Learning.pdf
│   └── reports
│       └── Relatório Técnico Parcial.pdf
├── instances
│   ├── CiscoSecureWorkload_22_networks
│   │   
│   └── my_testes
│       ├── cisco.txt
│       ├── Instances - Optimizing INT.xlsx
│       └── teste_dani.txt
├── results
│   ├── C_parsed_data
│   │   └── teste_dani_parsed.txt
│   ├── gurobi
│   │   └── py_parsed_data_gurobi_result.txt
│   └── py_parsed_data
│       ├── E_for_gurobi.pkl
│       ├── edges.csv
│       ├── paths_by_group.json
│       ├── S_for_gurobi.pkl
│       ├── teste_dani_parsed.txt
│       └── vertices.csv
├── src
│   ├── solver
│   │   ├── heuristics
│   │   │   ├── firsth_heuristic.py
│   │   │   ├── v1_primeira_heurística.py
│   │   │   └── v2_primeira_heurística.py
│   │   └── rodar_modelo.py
│   └── utils
│       ├── parse_edges.py
│       └── processar_grafo.c
├── README.md
└── structure.md
