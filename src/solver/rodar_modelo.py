# Or run with a specific K value (e.g., K=5)
#python3 src/solver/rodar_modelo.py results/parsed_data 5

# In src/solver/rodar_modelo.py
# arquivo: rodar_modelo.py

import gurobipy as gp
from gurobipy import GRB
import pickle
import os
import sys

import networkx as nx
import matplotlib.pyplot as plt
import random

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


# ==============================================================================
# Funções auxiliares
# ==============================================================================

def gerar_subcaminhos(s, K):
    subcaminhos = []
    for i in range(len(s)):
        for j in range(i + 1, min(i + K + 1, len(s) + 1)):
            sub = tuple(s[i:j])
            subcaminhos.append(sub)
    return subcaminhos

def gerar_conjunto_P(S, K):
    P = set()
    for s in S:
        P.update(gerar_subcaminhos(s, K))
    return list(P)

# ==============================================================================
# Função principal
# ==============================================================================

def resolver_modelo_cobertura(E, S, K):
    print("--- Iniciando a resolução do modelo ---")
    print(f"Grafo com {len(E)} arestas e {len(S)} caminhos.")
    
    P = gerar_conjunto_P(S, K)
    print(f"Total de subcaminhos únicos gerados (|P|): {len(P)}")
    
    try:
        m = gp.Model("cobertura_de_arestas")

        # Mapear índice -> subcaminho
        p_index = {i: p for i, p in enumerate(P)}

        # Variáveis binárias x[i]
        x = m.addVars(len(P), vtype=GRB.BINARY, name="x")

        # Objetivo: minimizar número de subcaminhos escolhidos
        m.setObjective(x.sum(), GRB.MINIMIZE)

        # Restrições: cada aresta deve ser coberta exatamente 1 vez
        for e in E:
            m.addConstr(
                gp.quicksum(x[i] for i, p in p_index.items() if e in p) == 1,
                name=f"cobertura_{e}"
            )

        print("Modelo construído. Iniciando otimização...\n")
        m.optimize()

        print("\n--- Resultados da Otimização ---")
        if m.Status == GRB.OPTIMAL:
            print("Solução ótima encontrada!")
            print(f"Valor da Função Objetivo: {m.ObjVal:.0f}\n")

            caminhos_escolhidos = [p_index[i] for i in p_index if x[i].X > 0.5]

            print(f"Número de subcaminhos escolhidos: {len(caminhos_escolhidos)}")
            max_len = max(len(p) for p in caminhos_escolhidos)
            print(f"Tamanho máximo de arestas em um subcaminho escolhido: {max_len}\n")

            print("Subcaminhos selecionados:")
            for i, p in enumerate(caminhos_escolhidos, 1):
                print(f"  {i}: {p}")
        else:
            print(f"Modelo não ótimo. Status: {m.Status}")

    except gp.GurobiError as e:
        print(f"Erro do Gurobi: {e.errno} - {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    caminhos_escolhidos = []
    if m.Status == GRB.OPTIMAL:
        caminhos_escolhidos = [p_index[i] for i in p_index if x[i].X > 0.5]
        ...
    return caminhos_escolhidos

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    # The script now expects the path to the parsed data directory as the first argument
    # and the value of K as the second (optional) argument.
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho para o diretório com os arquivos pickle.")
        print("Uso: python src/solver/rodar_modelo.py <diretorio_dos_dados> [K]")
        sys.exit(1)

    data_directory = sys.argv[1]
    
    E_path = os.path.join(data_directory, "E_for_gurobi.pkl")
    S_path = os.path.join(data_directory, "S_for_gurobi.pkl")

    if not (os.path.exists(E_path) and os.path.exists(S_path)):
        print(f"Erro: Arquivos pickle não encontrados nos caminhos esperados:")
        print(f"  - {os.path.abspath(E_path)}")
        print(f"  - {os.path.abspath(S_path)}")
        print("\nRode o script de parse primeiro. Exemplo:")
        print("python src/utils/parse_edges.py instances/my_testes/teste_dani.txt results/parsed_data")
        sys.exit(1)

    # Carregar os dados extraídos
    print(f"Carregando arquivos de {os.path.abspath(data_directory)}...")
    with open(E_path, "rb") as f:
        E = pickle.load(f)
    with open(S_path, "rb") as f:
        S = pickle.load(f)

    # Ler K da linha de comando (padrão = 7)
    # K is now the second argument (index 2)
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    print(f"Usando K = {K}")

    # Resolver modelo
    caminhos_otimos = resolver_modelo_cobertura(E, S, K)

    # Desenhar resultados lado a lado
    if caminhos_otimos:
        desenhar_resultados(E, S, caminhos_otimos)