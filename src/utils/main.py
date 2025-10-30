# run: python -m src.utils.main instances/my_testes/teste_dani.txt

import sys, os
from .file_parser import parse_file
from .exporters import export_results, export_txt_report, preparar_E_S

def main():
    if len(sys.argv) < 2:
        print("Uso: python src/utils/main.py <arquivo_edges> [output_dir]")
        sys.exit(1)

    filepath = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else "results/py_parsed_data"

    grafo, caminhos_por_grupo, vertices_set, grupo_to_arestas, linhas_lidas = parse_file(filepath)

    S = [caminho for cg in caminhos_por_grupo for caminho in cg.caminhos]
    exports = export_results(output_dir, grafo, caminhos_por_grupo, vertices_set)

    instance_name = os.path.splitext(os.path.basename(filepath))[0]
    report_file = export_txt_report(output_dir, instance_name, grafo, S)

    print("-" * 30)
    print(f"Arquivos de saída gerados em: {os.path.abspath(output_dir)}")
    for k, v in exports.items():
        print(f"  {k}: {os.path.abspath(v)}")
    print(f"  txt_report: {os.path.abspath(report_file)}")
    print("-" * 30)

    E, S = preparar_E_S(grafo, caminhos_por_grupo)

if __name__ == "__main__":
    main()