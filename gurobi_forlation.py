# Importação de bibliotecas
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

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
        for j in range(i + 1, min(i + K + 1, len(s) + 1)):
            # Forma o subcaminho como uma tupla de arestas
            sub = tuple(s[i:j])
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

# ==============================================================================
# Função Principal de Otimização com Gurobi
# ==============================================================================

def resolver_modelo_cobertura(E, S, K):
    """
    Resolve o modelo de otimização para cobertura de arestas.
    
    Args:
        E (set): Conjunto de todas as arestas do grafo. Ex: {(0,1), (1,2), ...}
        S (list): Lista de caminhos válidos. Ex: [[(0,1),(1,2)], [(0,3)]]
        K (int): Número máximo de arestas por subcaminho.
        
    Returns:
        None: Imprime os resultados da otimização.
    """
    print("--- Iniciando a resolução do modelo ---")
    
    # Gerar o conjunto P de todos os subcaminhos possíveis
    print(f"Gerando subcaminhos de tamanho máximo K={K}...")
    P = gerar_conjunto_P(S, K)
    print(f"Total de subcaminhos únicos gerados (|P|): {len(P)}")
    
    # Criar um dicionário para mapear cada subcaminho a um índice, se necessário
    # p_map = {p: i for i, p in enumerate(P)}

    try:
        # Inicializar o modelo Gurobi
        m = gp.Model("cobertura_de_arestas")
        
        # Adicionar as variáveis de decisão
        # xp = 1 se o subcaminho p é selecionado, 0 caso contrário.
        # Usamos o próprio subcaminho (tupla) como chave da variável.
        x = m.addVars(P, vtype=GRB.BINARY, name="x")
        
        # Definir a função objetivo
        # Minimizar o número total de subcaminhos usados
        m.setObjective(x.sum(), GRB.MINIMIZE)
        
        # Adicionar as restrições de cobertura
        # Cada aresta 'e' do grafo deve ser coberta por exatamente um subcaminho.
        # A expressão gp.quicksum(x[p] for p in P if e in p) é a tradução direta
        # da sua formulação: sum(delta_e,p * x_p for p in P).
        # O 'if e in p' atua como o parâmetro delta_e,p.
        for e in E:
           m.addConstr(gp.quicksum(x[p] for p in P if e in p) == 1, name=f"cobertura_{e}")
            
        """
        # Para cada aresta e, somamos x[p] de todos os subcaminhos p que contêm e
        for e in E:
            soma = 0
            for p in P:
                if e in p:
                    soma += x[p]
            # Adiciona a restrição de que a soma deve ser igual a 1
            m.addConstr(soma == 1, name=f"cobertura_{e}")

        """
        
        print("Modelo Gurobi construído. Iniciando otimização...")
        
        # Otimizar o modelo
        m.optimize()
        
        # Exibir os resultados
        print("\n--- Resultados da Otimização ---")
        if m.Status == GRB.OPTIMAL:
            print(f"Solução ótima encontrada!")
            print(f"Valor da Função Objetivo (subcaminhos usados): {m.ObjVal:.0f}\n")
            
            print("Subcaminhos selecionados:")
            count = 0
            for p in P:
                # Usamos uma pequena tolerância para checagem de valores binários
                if x[p].X > 0.5:
                    count += 1
                    print(f"  {count}: {p}")
        else:
            print(f"Não foi encontrada uma solução ótima. Status do Gurobi: {m.Status}")
            
    except gp.GurobiError as e:
        print(f"Erro do Gurobi: {e.errno} - {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

