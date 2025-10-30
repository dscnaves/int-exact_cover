def desenhar_resultados(E, S, caminhos_otimos):
    """
    Desenha lado a lado:
      - Grafo original com todos os caminhos pré-definidos (S), cada um com cor distinta.
      - Grafo com a solução ótima do Gurobi (caminhos_otimos), cada subcaminho com cor distinta.

    Args:
        E (set): conjunto de arestas (u,v)
        S (list): lista de caminhos, cada caminho é uma lista de arestas
        caminhos_otimos (list): lista de subcaminhos escolhidos pelo gurobi
    """
    # Criação do grafo base
    G = nx.DiGraph()
    G.add_edges_from(E)

    pos = nx.spring_layout(G, seed=42)  # layout fixo para consistência

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # =====================================================================
    # ESQUERDA: Grafo original com caminhos pré-definidos
    # =====================================================================
    ax = axes[0]
    ax.set_title("Grafo Original - Caminhos Pré-definidos (S)", fontsize=12)

    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightgray", ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)

    # Cada caminho em S recebe uma cor diferente
    colors = plt.cm.tab20.colors  # até 20 cores bem distintas
    for i, caminho in enumerate(S):
        cor = colors[i % len(colors)]
        nx.draw_networkx_edges(
            G, pos,
            edgelist=caminho,
            edge_color=[cor],
            width=2.5,
            arrows=True,
            ax=ax
        )

    # =====================================================================
    # DIREITA: Grafo com solução ótima do Gurobi
    # =====================================================================
    ax = axes[1]
    ax.set_title("Solução Ótima - Subcaminhos Escolhidos", fontsize=12)

    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightgray", ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)

    # Cada subcaminho escolhido recebe uma cor distinta
    for i, subcaminho in enumerate(caminhos_otimos):
        cor = colors[i % len(colors)]
        nx.draw_networkx_edges(
            G, pos,
            edgelist=subcaminho,
            edge_color=[cor],
            width=2.5,
            arrows=True,
            ax=ax
        )

    plt.tight_layout()
    plt.show()