# ==============================================================================
# Funções para Geração do Conjunto de Subcaminhos (P)
# ==============================================================================

def gerar_subcaminhos(s, K):
    """
    Gera todos os subcaminhos de tamanho <= K de um único caminho s.
    Um caminho 's' é uma lista de arestas, onde cada aresta é uma tupla (u, v).
    """
    subcaminhos = []
    # Para cada aresta do caminho s
    for i in range(len(s)):
        # O subcaminho se inicia na aresta i e finaliza na aresta j-1
        for j in range(i , min(i + K, len(s))):
            # Forma o subcaminho como uma tupla de arestas
            sub = tuple(s[i:j+1])
            subcaminhos.append(sub)
    return subcaminhos


def gerar_conjunto_P(S, K):
    """
    Gera o conjunto P de todos os subcaminhos válidos de tamanho máximo K
    a partir de um conjunto de caminhos S.
    """
    P = set()
    for s in S:
        # A propriedade de P ser um conjunto garante que não haja repetição
        P.update(gerar_subcaminhos(s, K))
    return list(P) # Retorna como lista para ter uma ordem definida

def heuristic_choose_subpath_by_num_not_covered_edges(G, P):
    """
    Algoritmo guloso para cobrir as arestas do grafo G com subcaminhos de P.
    
    G: conjunto de arestas do grafo (ex: {('A','B'), ('B','C')})
    P: lista de subcaminhos, onde cada subcaminho é uma tupla de arestas
       (ex: [(('A','B'),), (('A','B'),('B','C'))])
    """
    E = set(G)          # arestas do grafo
    covered = set()     # arestas já cobertas
    S_linha = []        # solução

    while covered != E:
        candidatos = []
        for sub in P:
            sub_set = set(sub)
            # arestas que ainda não foram cobertas por este subcaminho
            uncovered = sub_set - covered
            # só considera se cobre pelo menos 1 nova aresta
            # e não tem conflito (nenhuma aresta já coberta)
            if len(uncovered) > 0 and not (sub_set & covered):
                candidatos.append((sub, len(uncovered)))

        if not candidatos:
            print("Erro: não foi possível cobrir todas as arestas. Restam:", E - covered)
            return None

        # escolhe o subcaminho que cobre mais arestas não cobertas
        candidatos.sort(key=lambda x: x[1], reverse=True)
        escolhido = candidatos[0][0]

        S_linha.append(escolhido)
        covered.update(escolhido)

    return S_linha