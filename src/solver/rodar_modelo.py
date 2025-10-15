# Or run with a specific K value (e.g., K=5)
# python3 src/solver/rodar_modelo.py results/py_parsed_data 5

# In src/solver/rodar_modelo.py
# arquivo: rodar_modelo.py

import gurobipy as gp
from gurobipy import GRB
import pickle
import os
import sys
import time
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
def subcaminho_edges_to_vertices(sub):
    """
    Aceita sub como:
      - tupla/lista de arestas: [(u,v), (u2,v2), ...]  -> retorna [u, v, v2, ...]
      - tupla/lista de vértices: [v1, v2, v3, ...]     -> retorna [v1, v2, v3, ...]
      - caso ambíguo retorna None
    """
    if not sub:
        return []
    # detectar formato: elementos são pares (arestas) ou escalares (vértices)
    first = sub[0]
    # aresta-like
    if isinstance(first, (list, tuple)) and len(first) == 2:
        vertices = []
        try:
            u0, v0 = first
        except Exception:
            return None
        vertices.append(u0)
        current = v0
        vertices.append(current)
        for item in sub[1:]:
            if not (isinstance(item, (list, tuple)) and len(item) == 2):
                # mistura de formatos -> abortar inferência
                return None
            a, b = item
            if a != current:
                # desconexo no input; adicionamos ambos para não perder informação
                vertices.append(a)
                vertices.append(b)
                current = b
            else:
                vertices.append(b)
                current = b
        return vertices
    else:
        # assumimos lista de vértices
        try:
            return [int(x) for x in sub]
        except Exception:
            return None

def edges_string_from_sub(sub):
    """
    Produz string de arestas a partir do sub:
      - se sub contém arestas -> usa elas;
      - se sub contém vértices -> transforma em arestas consecutivas.
    """
    if not sub:
        return ""
    first = sub[0]
    edges = []
    if isinstance(first, (list, tuple)) and len(first) == 2:
        for (a, b) in sub:
            edges.append((a, b))
    else:
        # assumir vértices e criar pares consecutivos
        verts = list(sub)
        for i in range(len(verts) - 1):
            edges.append((verts[i], verts[i + 1]))
    return ", ".join(f"({a},{b})" for (a, b) in edges)

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

# -------------------------
# Resolução do modelo e gravação dos resultados em arquivo .txt
# -------------------------
def resolver_modelo_cobertura(E, S, K, output_dir=None, instance_id=None):
    """
    Constrói e resolve o modelo. Em seguida grava resultados em arquivo .txt em output_dir.
    Retorna lista de subcaminhos escolhidos (cada subcaminho é tuple de arestas ou vértices).
    """
    print("--- Iniciando a resolução do modelo ---")
    print(f"Grafo com {len(E)} arestas e {len(S)} caminhos.")
    P = gerar_conjunto_P(S, K)
    total_subcaminhos_gerados = len(P)
    print(f"Total de subcaminhos únicos gerados (|P|): {total_subcaminhos_gerados}")

    # preparacao do diretorio de saída
    if output_dir is None:
        output_dir = os.path.join("results", "gurobi")
    os.makedirs(output_dir, exist_ok=True)

    # definir nome do arquivo de saída
    if instance_id is None:
        instance_id = os.path.basename(os.path.abspath("."))  # fallback: nome do cwd
    safe_instance = instance_id.replace(" ", "_")
    out_path = os.path.join(output_dir, f"{safe_instance}_gurobi_result.txt")

    start_time = time.time()
    try:
        m = gp.Model("cobertura_de_arestas")
        p_index = {i: p for i, p in enumerate(P)}

        # Variáveis binárias
        x = m.addVars(len(P), vtype=GRB.BINARY, name="x")

        # Objetivo: minimizar número de subcaminhos selecionados
        m.setObjective(x.sum(), GRB.MINIMIZE)

        # Restrições: cada aresta deve ser coberta exatamente 1 vez
        # Nota: assume-se que 'p' pode ser uma sequência de arestas ou de vértices. Tentamos ambas.
        for e in E:
            # montar lista dos índices i cujo p cobre a aresta e
            inds = []
            for i, p in p_index.items():
                # se p contém arestas como tuplas (u,v)
                if p and isinstance(p[0], (list, tuple)) and len(p[0]) == 2:
                    if e in p:
                        inds.append(x[i])
                else:
                    # p é sequência de vértices -> checar pares consecutivos
                    verts = list(p)
                    for a_idx in range(len(verts) - 1):
                        if (verts[a_idx], verts[a_idx + 1]) == e:
                            inds.append(x[i])
                            break
            # adicionar a restrição
            m.addConstr(gp.quicksum(inds) == 1, name=f"cobertura_{e}")

        print("Modelo construído. Iniciando otimização...\n")
        m.optimize()

        end_time = time.time()
        total_runtime_wall = end_time - start_time

        # Coleta de informações do modelo
        status = m.Status
        status_str = status_to_string(status)
        objval = None
        objbound = None
        mipgap = None
        nodecount = None

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

        # montar texto de saída com a formatação solicitada
        lines = []
        lines.append("="*59)
        lines.append(f"Instância: {instance_id}")
        lines.append("="*59)
        lines.append("Resultados do Modelo Gurobi")
        lines.append("-"*60)

        # format helpers
        def l(label, value):
            # cria linha com pontos para alinhamento similar ao exemplo
            # comprimento fixo para label + value
            return f"• {label.ljust(35)}: {value}"

        # formata gap como percentagem com 2 casas (se houver)
        if mipgap is None:
            gap_str = "N/A"
        else:
            try:
                gap_str = f"{100.0 * float(mipgap):.2f}%"
            except Exception:
                gap_str = str(mipgap)

        lines.append(l("Valor da Função Objetivo........", f"{objval if objval is not None else 'N/A'}"))
        lines.append(l("Número de Subcaminhos Iniciais...", f"{total_subcaminhos_gerados}"))
        lines.append(l("Limite Inferior (Lower Bound)......", f"{objbound if objbound is not None else 'N/A'}"))
        lines.append(l("GAP.............................", gap_str))
        lines.append(l("Nós da Árvore de Decisão........", f"{nodecount if nodecount is not None else 0.0}"))
        lines.append(l("Tempo Total de Execução.........", f"{total_runtime_wall} segundos"))
        found_optimal = (status == GRB.OPTIMAL)
        lines.append(l("Solução Ótima Encontrada?.......", "SIM" if found_optimal else "NÃO"))
        lines.append(l("Status texto do Gurobi..........", status_str))
        lines.append("-"*60)
        lines.append("")
        lines.append("Subcaminhos Selecionados:")
        lines.append("-"*60)

        if caminhos_escolhidos:
            for idx, sub in enumerate(caminhos_escolhidos, start=1):
                vertices = subcaminho_edges_to_vertices(list(sub))
                if vertices is None:
                    vert_str = "(não foi possível inferir sequência de vértices)"
                    num_vertices = "N/A"
                else:
                    vert_str = "->".join(str(v) for v in vertices)
                    num_vertices = len(vertices)
                lines.append(f"subcaminho {idx} n°vertices ({num_vertices}): ({vert_str})")
                edges_str = edges_string_from_sub(sub)
                if edges_str:
                    lines.append(f"  arestas: {edges_str}")
                else:
                    lines.append(f"  arestas: (não foi possível inferir arestas)")
                lines.append("")  # linha em branco entre subcaminhos
        else:
            lines.append("Nenhum subcaminho foi selecionado pela solução (ou não há solução disponível).")

        lines.append("-"*60)
        lines.append("")
        lines.append("Fim do relatório")
        lines.append("="*59)
        lines.append("")

        # escrever arquivo
        with open(out_path, "w", encoding="utf-8") as fout:
            fout.write("\n".join(lines))

        print(f"\nResultados gravados em: {os.path.abspath(out_path)}")
        # também imprimir um sumário na saída padrão (primeiras linhas)
        print("\n--- Resumo ---")
        for ln in lines[:12]:
            print(ln)
        print("... (ver arquivo para detalhes completos)")

    except gp.GurobiError as e:
        print(f"Erro do Gurobi: {e.errno} - {e}")
        caminhos_escolhidos = []
    except Exception as e:
        end_time = time.time()
        total_runtime_wall = end_time - start_time
        print(f"Ocorreu um erro: {e}")
        caminhos_escolhidos = []

    return caminhos_escolhidos


# -------------------------
# Main
# -------------------------
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
        print("python src/utils/parse_edges.py instances/my_testes/teste_dani.txt results/py_parsed_data")
        sys.exit(1)

    print(f"Carregando arquivos de {os.path.abspath(data_directory)}...")
    with open(E_path, "rb") as f:
        E = pickle.load(f)
    with open(S_path, "rb") as f:
        S = pickle.load(f)

    K = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    print(f"Usando K = {K}")

    # tentar descobrir um instance_id mais informativo:
    instance_id = os.path.basename(os.path.abspath(data_directory))
    caminhos_otimos = resolver_modelo_cobertura(E, S, K, output_dir=os.path.join("results", "gurobi"), instance_id=instance_id)

    # mostrar figura (se existir solução)
    if caminhos_otimos:
        desenhar_resultados(E, S, caminhos_otimos)