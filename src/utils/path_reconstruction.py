from typing import List, Tuple
from collections import defaultdict

def reconstruir_caminhos_por_grupo(arestas_do_grupo: List[Tuple[int,int]]) -> List[List[Tuple[int,int]]]:
    """
    Dado um conjunto/lista de arestas (u,v) que pertencem a um mesmo grupo, tenta ordenar/encadear
    essas arestas em caminhos. Retorna lista de caminhos (cada caminho é lista de arestas).
    Estratégia:
      - monta digrafo local com adj-list e in-degree/out-degree (apenas considerando arestas do grupo)
      - encontra nós candidatos a início (in-degree == 0). Para cada início, anda encadeando até acabar.
      - se houver ciclos ou componentes disjunta do grafo, escolhe um nó não visitado e percorre até detectar repetição.
    """

    # Se a lista de arestas estiver vazia, retorna imediatamente uma lista vazia (não tem caminho a reconstruir)
    if not arestas_do_grupo:
        return []

    # defaultdict (biblioteca collections): é um dicionário especial que, ao acessar uma chave inexistente, associa a  chave a uma lista vazia ([])
    
    # "dicionário" de lista de adjacência ({1: [2, 3], 2: [4]})
    adj = defaultdict(list)
    # grau de entrada dos nós
    in_deg = defaultdict(int)
    # grau de saída dos nós
    out_deg = defaultdict(int)
    # conjunto de nós presentes no subgrafo
    nodes = set()
    
    # para cada tupla (u,v) pertecente a aresta_do_grupo
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
    cover_edges = set()

    def follow_from(start: int) -> List:
        """
        Função auxiliar que, dado um nó inicial (start), tenta construir um caminho encadeando arestas ainda não usadas
        Estratégia gulosa: sempre segue a primeira aresta disponível
        """
        # For each iteration, we need to reset visited edges and nodes -> if we don't all the egdes will belong online one path
        visited_edges = set()  # conjunto de arestas visitadas (u,v)
        visited_nodes = set()

        # lista guardará todas as arestas que formam o caminho a partir de start
        path = []
        u = start
        visited_nodes.add(u)
        # loop serve para seguir arestas sucessivas do nó atual até não haver mais caminhos não visitados
        while True:
            # procurar aresta u->v não usada
            encontrou = False

            # Percorre todos os vizinhos de u na lista de adjacência adj, se u não tiver vizinhos, retorna uma lista vazia para evitar erro
            for v in adj.get(u, []):

                # Verifica se a aresta (u,v) ainda não foi percorrida
                if (u,v) not in visited_edges:
                    if v not in visited_nodes:
                        # Marca a aresta como visitada e o próximo nó como também visitado
                        visited_edges.add((u,v))
                        cover_edges.add((u,v))
                        visited_nodes.add(v)
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
    remaining_edges = [e for e in arestas_do_grupo if e not in cover_edges]
    
    # --- Tratar componentes cíclicos/componentes isoladas ---

    # Para cada aresta restante, se ainda não visitada, comece por sua origem e siga
    for u,v in remaining_edges:
        if (u,v) in cover_edges:
            # pula para a próxima aresta do loop se essa já estiver sido visitada por iterações anteriores
            continue

        # Cria uma lista vazia p que vai guardar o caminho construído a partir da aresta (u,v)
        p = []

        # Inicializa cur_u como o nó atual
        cur_u = u

        # Marca a aresta (u,v) como visitada
        cover_edges.add((u,v))

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
                if (cur_u, nx) not in cover_edges:
                    
                    # Marca a aresta como visitada
                    cover_edges.add((cur_u, nx))

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