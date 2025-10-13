# Or run with a specific K value (e.g., K=5)
# python3 src/solver/rodar_modelo.py results/parsed_data 5

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



# -------------------------
# Helpers para formatação de saída
# -------------------------
def subcaminho_edges_to_vertices(edge_list):
    """
    edge_list: lista/tupla de arestas no formato (u,v)
    Retorna lista de vértices [v1, v2, v3, ...] ou None se não for possível inferir.
    """
    if not edge_list:
        return []
    vertices = []
    # assumimos que edge_list[0] = (u0, v0), etc.
    try:
        u0, v0 = edge_list[0]
    except Exception:
        # caso arestas estejam em formato inesperado, retornamos string
        return None

    vertices.append(u0)
    current = v0
    vertices.append(current)
    for (a, b) in edge_list[1:]:
        # verifique consistência
        if a != current:
            # tentativa simples: se (a,b) não conectar, ainda adicionamos a,b para não perder info
            vertices.append(a)
            vertices.append(b)
            current = b
        else:
            vertices.append(b)
            current = b
    return vertices

def status_to_string(status_code):
    mapping = {
        GRB.LOADED: "LOADED",
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
        GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT"
    }
    return mapping.get(status_code, f"STATUS_{status_code}")





# ==============================================================================
# Função principal: Resolução do modelo e gravação dos resultados em arquivo .txt
# ==============================================================================

def resolver_modelo_cobertura(E, S, K, output_dir=None, instance_id=None):
    """
    Constrói e resolve o modelo. Em seguida grava resultados em arquivo .txt em output_dir.
    Retorna lista de subcaminhos escolhidos (cada subcaminho é tuple de arestas).
    """
    print("--- Iniciando a resolução do modelo ---")
    print(f"Grafo com {len(E)} arestas e {len(S)} caminhos.")
    P = gerar_conjunto_P(S, K)
    print(f"Total de subcaminhos únicos gerados (|P|): {len(P)}")

    # preparacao do diretorio de saída
    if output_dir is None:
        output_dir = os.path.join("results", "gurobi")
    os.makedirs(output_dir, exist_ok=True)

    # definir nome do arquivo de saída
    if instance_id is None:
        instance_id = os.path.basename(os.path.abspath("."))  # fallback: nome do cwd
    safe_instance = instance_id.replace(" ", "_")
    out_path = os.path.join(output_dir, f"{safe_instance}_gurobi_result.txt")

    try:
        m = gp.Model("cobertura_de_arestas")
        p_index = {i: p for i, p in enumerate(P)}

        # Variáveis binárias
        x = m.addVars(len(P), vtype=GRB.BINARY, name="x")

        # Objetivo
        m.setObjective(x.sum(), GRB.MINIMIZE)

        # Restrições: cada aresta deve ser coberta exatamente 1 vez
        for e in E:
            m.addConstr(
                gp.quicksum(x[i] for i, p in p_index.items() if e in p) == 1,
                name=f"cobertura_{e}"
            )

        print("Modelo construído. Iniciando otimização...\n")
        m.optimize()

        # Coleta de informações do modelo
        status = m.Status
        status_str = status_to_string(status)
        objval = None
        objbound = None
        mipgap = None
        nodecount = None
        runtime = None

        if status in [GRB.OPTIMAL, GRB.SUBOPTIMAL, GRB.TIME_LIMIT, GRB.USER_OBJ_LIMIT]:
            try:
                objval = m.ObjVal
            except Exception:
                objval = None
        try:
            objbound = m.ObjBound
        except Exception:
            objbound = None
        try:
            mipgap = m.MIPGap
        except Exception:
            mipgap = None
        try:
            nodecount = m.NodeCount
        except Exception:
            nodecount = None
        try:
            runtime = m.Runtime
        except Exception:
            runtime = None

        # extrair solução (se houver)
        caminhos_escolhidos = []
        if status in [GRB.OPTIMAL, GRB.SUBOPTIMAL] or (hasattr(m, "ObjVal") and m.Status == GRB.OPTIMAL):
            # pegar x[i] com X > 0.5
            for i in p_index:
                try:
                    val = x[i].X
                except Exception:
                    val = 0
                if val > 0.5:
                    caminhos_escolhidos.append(p_index[i])

        # montar texto de saída
        lines = []
        lines.append(f"ID_instances (pasta_dados/instance_id): {instance_id}")
        lines.append(f"resultado da função objetivo: {objval if objval is not None else 'N/A'}")
        lines.append(f"n de subcaminhos gerados: {len(P)}")
        lines.append(f"limite inferior (bound limit): {objbound if objbound is not None else 'N/A'}")
        lines.append(f"GAP: {mipgap if mipgap is not None else 'N/A'}")
        lines.append(f"quantos nós da árvore de recursão/decisão que o gurobi percorreu: {nodecount if nodecount is not None else 'N/A'}")
        lines.append(f"tempo demorado para o gurobi chegar nessa solução: {runtime if runtime is not None else 'N/A'} (segundos)")
        lines.append(f"Status numérico do Gurobi: {status}")
        lines.append(f"Status texto do Gurobi: {status_str}")
        found_optimal = (status == GRB.OPTIMAL)
        lines.append(f"a solução ótima foi encontrada?: {'Sim' if found_optimal else 'Não'}")
        lines.append("")

        # solução ótima encontrada e detalhamento dos subcaminhos
        lines.append("solução ótima encontrada (lista de subcaminhos):")
        if caminhos_escolhidos:
            lines.append(f"número de subcaminhos escolhidos: {len(caminhos_escolhidos)}")
            for idx, sub in enumerate(caminhos_escolhidos, start=1):
                # sub é uma tupla de arestas (u,v)
                vertices = subcaminho_edges_to_vertices(list(sub))
                if vertices is None:
                    vert_str = "(não foi possível inferir sequência de vértices)"
                else:
                    vert_str = "->".join(str(v) for v in vertices)
                lines.append(f"subcaminho {idx} n°vertices ({len(vertices) if vertices is not None else 'N/A'}): ({vert_str})")
                # também opcional: listar as arestas
                edges_str = ", ".join(f"({a},{b})" for (a, b) in sub)
                lines.append(f"  arestas: {edges_str}")
                lines.append("")  # linha em branco entre subcaminhos
        else:
            lines.append("Nenhum subcaminho foi selecionado pela solução (ou não há solução disponível).")

        # escrever arquivo
        with open(out_path, "w", encoding="utf-8") as fout:
            fout.write("\n".join(lines))

        print(f"\nResultados gravados em: {os.path.abspath(out_path)}")
        # também imprimir um sumário na saída padrão
        print("\n--- Resumo ---")
        for ln in lines[:12]:
            print(ln)
        print("... (ver arquivo para detalhes completos)")

    except gp.GurobiError as e:
        print(f"Erro do Gurobi: {e.errno} - {e}")
        caminhos_escolhidos = []
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        caminhos_escolhidos = []

    return caminhos_escolhidos

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
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

    print(f"Carregando arquivos de {os.path.abspath(data_directory)}...")
    with open(E_path, "rb") as f:
        E = pickle.load(f)
    with open(S_path, "rb") as f:
        S = pickle.load(f)

    K = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    print(f"Usando K = {K}")

    # tentar descobrir um instance_id mais informativo:
    # se os pickles foram gerados a partir de um arquivo original, talvez exista um nome embutido.
    # aqui usamos o nome da pasta como ID; você pode passar um terceiro argumento com o nome da instância.
    instance_id = os.path.basename(os.path.abspath(data_directory))
    caminhos_otimos = resolver_modelo_cobertura(E, S, K, output_dir=os.path.join("results", "gurobi"), instance_id=instance_id)

    # mostrar figura (se existir solução)
    if caminhos_otimos:
        desenhar_resultados(E, S, caminhos_otimos)