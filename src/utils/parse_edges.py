
# Comando para fazer código rodar: python src/utils/parse_edges.py <arquivo_edges> [output_dir]
# python3 src/utils/parse_edges.py instances/my_testes/teste_dani.txt results/py_parsed_data
# or python3 src/utils/parse_edges.py instances/my_testes/teste_dani.txt

"""
Parser de arquivo edges_to_ports_*.anon
- Extrai vértices, arestas e grupos (caminhos pré-definidos via código tipo `1p6-10`).
- Reconstrói caminhos por grupo (encadeando arestas quando possível).
- Exporta arquivos: edges.csv, vertices.csv, paths.json e uma versão pickle com S para uso com Gurobi.
- Prepara E (set de arestas) e S (lista de caminhos) para integração com seu código Gurobi.
"""

from dataclasses import dataclass, asdict       # Facilita a criação de classes
from typing import List, Tuple, Dict, Set
import csv      # Biblioteca nativa do Python para ler e escrever arquivos no formato CSV
import json     # Biblioteca para trabalhar com o formato JSON - representar dados com estruturas hierarquicas
import pickle
import sys      # Pegar argumentos de linha de comando
from collections import defaultdict, deque
import os

# -----------------------
# Structs with dataclasses
# -----------------------
@dataclass
class Aresta:
    origem: int
    destino: int

@dataclass
class Grafo:
    num_vertices: int
    num_arestas: int
    arestas: List[Aresta]

@dataclass
class CaminhosGrupo:
    grupo_id: str
    caminhos: List[List[Tuple[int, int]]]  # cada caminho é lista de arestas (tuplas (u,v))

# -----------------------
# Extrair prefixo do grupo
# -----------------------
def extrai_grupos(token: str) -> str:
    """
    Recebe um token do tipo '1p6-10' ou '915p6-10785' e retorna '1p6' ou '915p6'.
    Se o token não tiver '-', retorna-o inteiro sem espaços.
    """

    token = token.strip()   # Remove espaços em branco do começo e do fim da string: "   1p6-10   ".strip()   # → "1p6-10"

    if not token:
        return None
    if '-' in token:
        partes = token.split('-', 1)   # "1p6-10".split('-', 1)  # → ["1p6", "10"]
        prefixo = partes[0]           # pega só o primeiro
        return prefixo
    return token

def parse_line(line: str):
    """
    Fragmenta uma linha do tipo:
    g21    20    23    1p6-10,3p17-14
    Retorna (nome_grafo, origem:int, destino:int, [grupos])
    Ex.: ("g21", 20, 23, ["1p6", "3p17"])
    """
    # .strip() → remove espaços/brancos extras do início e fim da linha
    # .split() → sem argumento, divide a string em uma lista de pedaços
    parts = line.strip().split()
    if len(parts) < 4:
        raise ValueError(f"Linha com formato inesperado: {line!r}")
    
    nome = parts[0]
    try:
        origem = int(parts[1])
        destino = int(parts[2])
    except ValueError as e:
        raise ValueError(f"Erro ao converter origem/destino em inteiro na linha: {line!r}") from e
    
    # Caso houver espaços entre grupos, elimina: "1p6-10,   3p17-14" → "1p6-10,3p17-14"
    grupos_raw = " ".join(parts[3:])
    
    # Divide a string em pedaços usando vírgula
    partes = grupos_raw.split(',')

    # Cria uma lista nova para guardar os tokens tratados
    grupos_tokens = []

    # Para cada pedaço obtido
    for t in partes:
        # Remove espaços no começo e no fim
        token_limpo = t.strip()

        # Se não for vazio, adiciona à lista final
        if token_limpo:
            grupos_tokens.append(token_limpo)
    
    # Cria uma lista nova para guardar os grupos extraídos
    grupos_ids = []

    # Para cada token da lista de grupos
    for t in grupos_tokens:
        # Aplica a função extrai_grupos
        grupo = extrai_grupos(t)

        # Se o resultado não for None, adiciona à lista final
        if grupo is not None:
            grupos_ids.append(grupo)

    return nome, origem, destino, grupos_ids

def reconstruir_caminhos_por_grupo(arestas_do_grupo: List[Tuple[int,int]]) -> List[List[Tuple[int,int]]]:
    """
    Dado um conjunto de arestas (u,v) que pertencem a um mesmo grupo, tenta ordenar/encadear
    essas arestas em caminhos. Retorna lista de caminhos (cada caminho é lista de arestas).
    Estratégia:
      - monta digrafo local com adj-list e in-degree/out-degree (apenas considerando arestas do grupo)
      - encontra nós candidatos a início (in-degree == 0). Para cada início, anda encadeando até acabar.
      - se houver ciclos ou componentes disjunta do grafo, escolhe um nó não visitado e percorre até detectar repetição.
    """

    # Se a lista de arestas estiver vazia, retorna imediatamente uma lista vazia (não tem caminho a reconstruir)
    if not arestas_do_grupo:
        return []

    # defaultdict (biblioteca collections): é um dicionário especial que, ao acessar uma chave inexistente, associa a  cahve a uma lista vazia ([])
    
    # "dicionário" de lista de adjacência ({1: [2, 3], 2: [4]})
    adj = defaultdict(list)
    # grau de entrada dos nós
    in_deg = defaultdict(int)
    # grau de saída dos nós
    out_deg = defaultdict(int)
    # conjunto de nós presentes no subgrafo
    nodes = set()
    
    for u, v in arestas_do_grupo:
        adj[u].append(v)
        out_deg[u] += 1
        in_deg[v] += 1
        nodes.add(u); nodes.add(v)

    # Cria uma lista vazia para guardar os nós iniciais
    starts = []

    # Percorre todos os nós do subgrafo
    for n in nodes:
        # Obtém o grau de entrada, 0 se não estiver no dicionário
        # "dicionario.get(chave, valor_padrao) → retorna chave ou zero se n não existir em in_deg"
        entrada = in_deg.get(n, 0)

        # Obtém o grau de saída, 0 se não estiver no dicionário
        saida = out_deg.get(n, 0)

        # Verifica se é nó inicial: in-degree == 0 e out-degree > 0
        if entrada == 0 and saida > 0:
            # Adiciona à lista de starts
            starts.append(n)

    # lista onde os caminhos reconstruídos serão armazenados
    caminhos = []
    visited_edges = set()  # conjunto de arestas visitadas (u,v)

    def follow_from(start):
        """
        Função auxiliar que, dado um nó inicial (start), tenta construir um caminho encadeando arestas ainda não usadas
        Estratégia gulosa: sempre segue a primeira aresta disponível
        """

        # lista guardará todas as arestas que formam o caminho a partir de start
        path = []
        u = start
        # loop serve para seguir arestas sucessivas do nó atual até não haver mais caminhos não visitados
        while True:
            # procurar aresta u->v não usada
            encontrou = False

            # Percorre todos os vizinhos de u na lista de adjacência adj, se u não tiver vizinhos, retorna uma lista vazia para evitar erro
            for v in adj.get(u, []):

                # Verifica se a aresta (u,v) ainda não foi percorrida
                if (u,v) not in visited_edges:
                    # Marca a aresta como visitada
                    visited_edges.add((u,v))
                    # Adiciona a aresta (u,v) ao caminho que estamos construindo
                    path.append((u,v))
                    # Atualiza o nó atual para o próximo nó no caminho
                    u = v
                    # Sinaliza que conseguimos seguir por uma aresta válida
                    encontrou = True
                    # Sai do for porque seguimos apenas a primeira aresta disponível (estratégia gulosa)
                    break

            # Se não encontramos nenhuma aresta não visitada saindo de u, significa que o caminho acabou
            if not encontrou:
                break
        return path

    # Para cada nó inicial, chama follow_from
    for s in starts:
        p = follow_from(s)

        # Se conseguiu formar um caminho (p não vazio), adiciona em caminhos
        if p:
            caminhos.append(p)

    # Monta uma lista de arestas que ainda não foram visitadas (podem estar em ciclos ou componentes não conectados a um nó inicial em caso de caminhos "com ramificações")
    remaining_edges = [e for e in arestas_do_grupo if e not in visited_edges]
    
    # --- Tratar componentes cíclicos/ramificados ---

    # Para cada aresta restante, se ainda não visitada, comece por sua origem e siga
    for u,v in remaining_edges:
        if (u,v) in visited_edges:
            # pula para a próxima aresta do loop se essa já estiver visitada
            continue

        # Cria uma lista vazia p que vai guardar o caminho construído a partir da aresta (u,v)
        p = []

        # Inicializa cur_u como o nó atual
        cur_u = u

        # Marca a aresta (u,v) como visitada
        visited_edges.add((u,v))

        # Adiciona (u,v) ao caminho p
        p.append((u,v))

        # Atualiza o nó atual para o destino da aresta (u,v)
        cur_u = v

        # percorrer o caminho a partir de cur_u
        while True:
            encontrou = False

            # Percorre todos os vizinhos (nx) do nó atual cur_u
            for nx in adj.get(cur_u, []):

                # Verifica se a aresta ainda não foi visitada
                if (cur_u, nx) not in visited_edges:
                    
                    # Marca a aresta como visitada
                    visited_edges.add((cur_u, nx))

                    # Adiciona a aresta ao caminho atual p
                    p.append((cur_u, nx))
                    
                    # Atualiza o nó atual para o próximo nó do caminho
                    cur_u = nx

                    # Indica que seguimos por uma aresta válida
                    encontrou = True

                    # Sai do for porque seguimos apenas a primeira aresta disponível
                    break
            if not encontrou:
                break
        caminhos.append(p)

    # Retornar caminhos reconstruídos
    return caminhos

# -----------------------
# Parser principal
# -----------------------
def parse_file(filepath: str):
    """
    A função vai ler um arquivo de arestas, extrair vértices, grupos e reconstruir caminhos por grupo
    Parâmetro filepath é uma string com o caminho do arquivo a ser lido.
    """

    # guardar todos os vértices únicos encontrados no arquivo
    vertices: Set[int] = set()
    # armazenará objetos Aresta
    arestas_list: List[Aresta] = []
    # dicionário que mapeia cada grupo (str) para uma lista de arestas (u,v)
    grupo_to_arestas: Dict[str, List[Tuple[int,int]]] = defaultdict(list)
    # quantas linhas válidas foram processadas do arquivo
    linhas_lidas = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        # itera linha por linha do arquivo. Cada linha é uma string
        for raw in f:
            # Remove espaços em branco e quebras de linha do início e fim da linha
            line = raw.strip()

            # Ignora linhas vazias
            if not line:
                continue
            # pular linhas de comentário (se houver) — aqui assumimos que linhas válidas começam com 'g' ou letra
            try:
                nome, u, v, grupos = parse_line(line)
            
            # Se a linha não tiver o formato esperado, um ValueError é lançado, a linha é ignorada e segue para próxima
            except ValueError as e:
                print(f"AVISO: linha ignorada ({e})")
                continue

            linhas_lidas += 1

            # Adiciona os vértices u e v ao conjunto de vértices
            vertices.add(u); vertices.add(v)
            # Cria um objeto Aresta com os vértices (u,v) e adiciona à lista arestas_list
            arestas_list.append(Aresta(u, v))
            
            # Para cada grupo g ao qual a aresta pertence
            for g in grupos:
                # Adiciona a aresta (u,v) à lista correspondente no dicionário grupo_to_arestas
                grupo_to_arestas[g].append((u, v))

    # construir Grafo
    grafo = Grafo(num_vertices=len(vertices), num_arestas=len(arestas_list), arestas=arestas_list)

    # Cria lista caminhos_por_grupo para armazenar caminhos reconstruídos para cada grupo
    caminhos_por_grupo: List[CaminhosGrupo] = []
    
    # Itera sobre cada grupo do dicionário grupo_to_arestas
    for grupo_id, arestas in grupo_to_arestas.items():
        
        # retorna lista de caminhos (listas de arestas encadeadas)
        caminhos = reconstruir_caminhos_por_grupo(arestas)
        
        # Adiciona um objeto CaminhosGrupo com grupo_id e os caminhos encontrados à lista final
        caminhos_por_grupo.append(CaminhosGrupo(grupo_id=grupo_id, caminhos=caminhos))

    return grafo, caminhos_por_grupo, vertices, grupo_to_arestas, linhas_lidas

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

# -----------------------
# main
# -----------------------

def main():
    # sys.argv é uma lista com tudo que foi digitado no terminal
    if len(sys.argv) < 2:
        print("Uso: python src/utils/parse_edges.py <arquivo_edges> [output_dir]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # If an output directory is provided, use it. Otherwise, default to 'results/py_parsed_data'.
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else "results/py_parsed_data"

    print(f"Lendo arquivo: {filepath} ...")

    # Chama a função parse_file, que abre o arquivo, lê cada linha, cria os vértices, arestas e grupos
    grafo, caminhos_por_grupo, vertices_set, grupo_to_arestas, linhas_lidas = parse_file(filepath)

    S = []
    for cg in caminhos_por_grupo:
        for caminho in cg.caminhos:
            S.append(caminho)

    # exporta os resultados para arquivos (CSV, JSON, pickle)
    exports = export_results(output_dir, grafo, caminhos_por_grupo, vertices_set)

    instance_name = os.path.splitext(os.path.basename(filepath))[0]
    report_file = export_txt_report(output_dir, instance_name, grafo, S)
    
    print("-" * 30)
    print(f"Arquivos de saída gerados em: {os.path.abspath(output_dir)}")
    print("-" * 30)
    for k, v in exports.items():
        print(f"  {k}: {os.path.abspath(v)}")
    print(f"  txt_report: {os.path.abspath(report_file)}")
    print("-" * 30)

    # preparar E e S para rodar com Gurobi
    E, S = preparar_E_S(grafo, caminhos_por_grupo)

if __name__ == "__main__":
    main()
