from typing import List, Tuple, Dict, Set
from collections import defaultdict
from .graph_structs import Aresta, Grafo, CaminhosGrupo  
from .path_reconstruction import reconstruir_caminhos_por_grupo 

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
