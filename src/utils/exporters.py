import os, csv, json, pickle
from .graph_structs import Grafo, CaminhosGrupo  
from typing import List, Tuple, Set

# -----------------------------------------------------
# To generate the .txt report
# -----------------------------------------------------
def export_txt_report(output_dir: str, instance_name: str, grafo: Grafo, all_paths: List[List[Tuple[int, int]]]):
    """
    Gera um relatório .txt sumarizando os dados do grafo e os caminhos.
    """
    # Define o nome do arquivo de saida
    report_path = os.path.join(output_dir, f"{instance_name}_parsed.txt")
    
    # Garante que o diretório de saída exista
    os.makedirs(output_dir, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("===========================================================\n")
        f.write(f" Instância: {instance_name}\n")
        f.write("===========================================================\n")
        f.write(" Resultados da Extração de Caminhos\n")
        f.write("------------------------------------------------------------\n")
        
        # Escreve o sumário com formatação alinhada
        f.write(f"{'Número Total de Vértices........':<35}: {grafo.num_vertices}\n")
        f.write(f"{'Número Total de Arestas.........':<35}: {grafo.num_arestas}\n")
        f.write(f"{'Número de Caminhos..............':<35}: {len(all_paths)}\n\n")

        f.write("------------------------------------------------------------\n")
        f.write("      CAMINHOS GERADOS\n")
        f.write("------------------------------------------------------------\n")

        if not all_paths:
            f.write("Nenhum caminho foi gerado.\n")
        
        # Itera sobre cada caminho para escrevê-lo no arquivo
        for i, path_edges in enumerate(all_paths, 1):
            if not path_edges:
                continue

            # Reconstrói a sequência de vértices a partir das arestas
            # Ex: [(2,5), (5,10)] -> [2, 5, 10]
            nodes_in_path = [path_edges[0][0]] + [v for u, v in path_edges]
            
            # Formata a string do caminho: (2->5->10)
            path_str = "->".join(map(str, nodes_in_path))
            
            # Formata a string das arestas: (2,5), (5,10)
            edges_str = ", ".join(map(str, path_edges))
            
            # Escreve as informações do subcaminho
            f.write(f"subcaminho {i} - n°vertices ({len(nodes_in_path)}): ({path_str})\n")
            f.write(f"  arestas: {edges_str}\n\n")

        f.write("------------------------------------------------------------\n\n")
        f.write(" Fim do relatório \n")
        f.write("===========================================================\n")
        
    # Retorna o caminho do relatório criado para poder ser impresso no final
    return report_path

# -----------------------
# Exportação e integração com Gurobi
# -----------------------
def export_results(output_dir: str, grafo: Grafo, caminhos_por_grupo: List[CaminhosGrupo], vertices_set: Set[int]):
    """
    Essa função prepara arquivos que depois podem ser lidos pelo solver Gurobi.
    Organiza as informações em arquivos para não sr necessário extrair novamente a cada interação da formulação do GUrobi.
    """
    
    # --- Cria o diretório output_dir ---
    os.makedirs(output_dir, exist_ok=True)
    
    # --- Export edges para CSV ---

    # junta diretório + nome do arquivo
    edges_csv = os.path.join(output_dir, "edges.csv")
    
    with open(edges_csv, 'w', newline='', encoding='utf-8') as f:
        # Cria um objeto escritor CSV que escreve no arquivo f
        writer = csv.writer(f)
        # Escreve a primeira linha (cabeçalho do CSV)
        writer.writerow(["origem","destino"])
        # Para cada aresta do grafo, escreve sua origem e destino no CSV
        for a in grafo.arestas:
            writer.writerow([a.origem, a.destino])

    # --- Export vertices para CSV ---
    vertices_csv = os.path.join(output_dir, "vertices.csv")
    with open(vertices_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["vertice"])
        for v in sorted(vertices_set):
            writer.writerow([v])

    # --- Export paths to JSON ---
    
    # caminho do arquivo JSON
    paths_json = os.path.join(output_dir, "paths_by_group.json")
    
    # cria um dicionário vazio
    json_data = {}
    for cg in caminhos_por_grupo:
        # cada caminho é lista de pares -> convert to list
        """
        Exemplo:
        {
        "g1": [[[1,2], [2,3]], [[4,5]]],
        "g2": [[[6,7], [7,8], [8,9]]]
        }
        """
        json_data[cg.grupo_id] = [ [ [u,v] for (u,v) in caminho ] for caminho in cg.caminhos ]
    
    with open(paths_json, 'w', encoding='utf-8') as f:
        # salva o dicionário
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    # --- Export a python-pickle com lista S pronta para Gurobi (S = lista de caminhos; cada caminho é lista de arestas (u,v)) ---

    # Cria lista S contendo todos os caminhos de todos os grupos
    S = []
    for cg in caminhos_por_grupo:
        for caminho in cg.caminhos:
            S.append(caminho)

    # montar caminho do arquivo
    pickle_path = os.path.join(output_dir, "S_for_gurobi.pkl")
    with open(pickle_path, 'wb') as f:
        # salva S no arquivo
        pickle.dump(S, f)

    # Cria o conjunto E com todas as arestas do grafo
    E = set((a.origem, a.destino) for a in grafo.arestas)
    with open(os.path.join(output_dir, "E_for_gurobi.pkl"), 'wb') as f:
        # salva E no arquivo
        pickle.dump(E, f)

    # --- Retornar caminhos dos arquivos ---
    return {
        "edges_csv": edges_csv,
        "vertices_csv": vertices_csv,
        "paths_json": paths_json,
        "S_pickle": pickle_path,
        "E_pickle": os.path.join(output_dir, "E_for_gurobi.pkl")
    }

# -----------------------
# Função para preparar E e S para uso com a função Gurobi
# -----------------------
def preparar_E_S(grafo: Grafo, caminhos_por_grupo: List[CaminhosGrupo]):
    
    # conjunto E contém todas as arestas do grafo
    E = set((a.origem, a.destino) for a in grafo.arestas)
    # Montar S: lista de caminhos (cada caminho é lista de arestas (u,v))
    S = []
    for cg in caminhos_por_grupo:

        # Para o caso de um mesmo grupo "1p4" tiver mais de um caminho
        """
        EXEMPLO: cg.caminhos = [
            [(1,2), (2,3)],     # caminho 1
            [(5,6), (6,7), (7,8)]  # caminho 2
        ]
        """
        for caminho in cg.caminhos:
            # cada caminho é lista de (u,v)
            S.append(caminho)
    return E, S