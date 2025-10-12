def guloso_cobertura(G, S, K):
    """
    Algoritmo Guloso de Cobertura por Subcaminhos

    Parâmetros:
        G : tuple
            Grafo direcionado representado como (V, E), onde
            V = conjunto de vértices, cada vértice v representado por uma str
            E = conjunto de arestas, cada aresta representada por (tuplas (u,v))
        S : list
            Lista de caminhos, cada caminho é uma lista de arestas [(u1,v1), (u2,v2), ...]
        K : int
            Capacidade máxima de arestas por subcaminho

    Retorna:
        S_linha : list
            Lista de subcaminhos selecionados, que cobrem todas as arestas exatamente uma vez
    """

    V, E = G
    arestas_nao_cobertas = set(E)   # conjunto de arestas que ainda precisam ser cobertas
    S_linha = []                    # conjunto solução de subcaminhos

    # enquanto houver arestas não cobertas
    while arestas_nao_cobertas:
        melhor_subcaminho = None
        melhor_cobertura = 0

        # percorre todos os caminhos originais
        for s in S:
            n = len(s)

            # gera subcaminhos que vão da aresta i até a aresta j de tamanho até K
            for i in range(n):
                for j in range(i, min(i + K, n)):
                    sub = s[i:j+1]  # subcaminho

                    # verifica se todas as arestas do sub ainda estão descobertas
                    if all(e in arestas_nao_cobertas for e in sub):
                        cobertura_atual = len(sub)

                        # escolhe o subcaminho que cobre mais arestas
                        if cobertura_atual > melhor_cobertura:
                            melhor_subcaminho = sub
                            melhor_cobertura = cobertura_atual

        # se não foi possível encontrar subcaminho válido
        if melhor_subcaminho is None:
            raise ValueError("Não foi possível cobrir todas as arestas com os caminhos fornecidos.")

        # adiciona o subcaminho à solução
        S_linha.append(melhor_subcaminho)

        # remove as arestas cobertas da lista de pendentes
        for e in melhor_subcaminho:
            arestas_nao_cobertas.discard(e)

    return S_linha
