#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// --- ESTRUTURAS DE DADOS ---

// Estrutura para representar uma aresta do grafo
typedef struct {
    int origem;
    int destino;
} Aresta;

// Estrutura para representar um Caminho/Grupo pré-definido
// Ele contém um nome (ex: "1p6") e uma lista de arestas que pertencem a ele
typedef struct {
    char *nome;                // Nome do caminho (ex: "1p6")
    Aresta *arestas;           // Array dinâmico de arestas neste caminho
    int num_arestas;           // Número atual de arestas
    int capacidade_arestas;    // Capacidade alocada para o array de arestas
} Caminho;

// Estrutura para representar o grafo principal e os caminhos
typedef struct {
    // Vértices são gerenciados dinamicamente, contamos os únicos no final
    int num_vertices_unicos;
    
    // Armazenamento de todas as arestas lidas
    Aresta *arestas_todas;
    int num_arestas_todas;
    int capacidade_arestas_todas;

    // Armazenamento de todos os caminhos/grupos encontrados
    Caminho *caminhos;
    int num_caminhos;
    int capacidade_caminhos;

} Grafo;

// --- PROTÓTIPOS DAS FUNÇÕES ---

void adicionarArestaAoCaminho(Grafo *g, const char *nome_caminho, Aresta aresta);
void processarArquivo(FILE *arquivo, Grafo *g);
void calcularVerticesUnicos(Grafo *g);
void escreverRelatorio(const Grafo *g, const char *nome_arquivo_saida);
void liberarMemoria(Grafo *g);

// --- FUNÇÃO PRINCIPAL ---

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <nome_do_arquivo_de_entrada>\n", argv[0]);
        return 1;
    }

    FILE *arquivo = fopen(argv[1], "r");
    if (arquivo == NULL) {
        perror("Erro ao abrir o arquivo de entrada");
        return 1;
    }

    // Inicializa a estrutura principal do grafo
    Grafo grafo = {0};

    printf("Processando arquivo '%s'...\n", argv[1]);
    processarArquivo(arquivo, &grafo);
    fclose(arquivo);

    printf("Calculando vértices únicos...\n");
    calcularVerticesUnicos(&grafo);

    const char *arquivo_saida = "relatorio_grafo.txt";
    printf("Escrevendo relatório para '%s'...\n", arquivo_saida);
    escreverRelatorio(&grafo, arquivo_saida);

    printf("Limpeza de memória...\n");
    liberarMemoria(&grafo);
    
    printf("Processo concluído com sucesso!\n");

    return 0;
}

// --- IMPLEMENTAÇÃO DAS FUNÇÕES ---

/**
 * Adiciona uma aresta a um caminho específico. Se o caminho não existir, ele é criado.
 */
void adicionarArestaAoCaminho(Grafo *g, const char *nome_caminho, Aresta aresta) {
    // 1. Procura se o caminho já existe
    for (int i = 0; i < g->num_caminhos; i++) {
        if (strcmp(g->caminhos[i].nome, nome_caminho) == 0) {
            // Se o array de arestas do caminho está cheio, realoca
            if (g->caminhos[i].num_arestas >= g->caminhos[i].capacidade_arestas) {
                g->caminhos[i].capacidade_arestas = g->caminhos[i].capacidade_arestas == 0 ? 10 : g->caminhos[i].capacidade_arestas * 2;
                g->caminhos[i].arestas = realloc(g->caminhos[i].arestas, g->caminhos[i].capacidade_arestas * sizeof(Aresta));
            }
            g->caminhos[i].arestas[g->caminhos[i].num_arestas++] = aresta;
            return;
        }
    }

    // 2. Se não encontrou, cria um novo caminho
    // Se o array de caminhos está cheio, realoca
    if (g->num_caminhos >= g->capacidade_caminhos) {
        g->capacidade_caminhos = g->capacidade_caminhos == 0 ? 10 : g->capacidade_caminhos * 2;
        g->caminhos = realloc(g->caminhos, g->capacidade_caminhos * sizeof(Caminho));
    }

    // Configura o novo caminho
    Caminho *novo_caminho = &g->caminhos[g->num_caminhos++];
    novo_caminho->nome = strdup(nome_caminho);
    novo_caminho->num_arestas = 0;
    novo_caminho->capacidade_arestas = 10; // Capacidade inicial
    novo_caminho->arestas = malloc(novo_caminho->capacidade_arestas * sizeof(Aresta));
    
    // Adiciona a aresta ao novo caminho
    novo_caminho->arestas[novo_caminho->num_arestas++] = aresta;
}

/**
 * Lê o arquivo linha por linha e preenche as estruturas de dados.
 */
void processarArquivo(FILE *arquivo, Grafo *g) {
    char linha[4096]; // Buffer grande para linhas longas
    char nome_grafo_dummy[256];
    
    while (fgets(linha, sizeof(linha), arquivo) != NULL) {
        Aresta aresta_atual;
        char caminhos_str[3500];

        // Tenta parsear os 3 primeiros campos
        if (sscanf(linha, "%s %d %d %s", nome_grafo_dummy, &aresta_atual.origem, &aresta_atual.destino, caminhos_str) != 4) {
            continue; // Pula linha mal formatada
        }

        // Adiciona a aresta à lista geral de arestas
        if (g->num_arestas_todas >= g->capacidade_arestas_todas) {
            g->capacidade_arestas_todas = g->capacidade_arestas_todas == 0 ? 2000 : g->capacidade_arestas_todas * 2;
            g->arestas_todas = realloc(g->arestas_todas, g->capacidade_arestas_todas * sizeof(Aresta));
        }
        g->arestas_todas[g->num_arestas_todas++] = aresta_atual;

        // Processa a string de caminhos (ex: "1p6-10,3p17-14")
        char *token = strtok(caminhos_str, ",");
        while (token != NULL) {
            // Encontra o hífen para separar o nome do caminho do número de pacotes
            char *hifen = strchr(token, '-');
            if (hifen != NULL) {
                *hifen = '\0'; // Corta a string no hífen
                adicionarArestaAoCaminho(g, token, aresta_atual);
            }
            token = strtok(NULL, ",");
        }
    }
}

/**
 * Calcula o número de vértices únicos a partir da lista de todas as arestas.
 */
void calcularVerticesUnicos(Grafo *g) {
    if (g->num_arestas_todas == 0) {
        g->num_vertices_unicos = 0;
        return;
    }

    int capacidade = g->num_arestas_todas * 2;
    int *vertices = malloc(capacidade * sizeof(int));
    int count = 0;

    for (int i = 0; i < g->num_arestas_todas; i++) {
        // Checa origem
        int achou = 0;
        for (int j = 0; j < count; j++) {
            if (vertices[j] == g->arestas_todas[i].origem) {
                achou = 1;
                break;
            }
        }
        if (!achou) vertices[count++] = g->arestas_todas[i].origem;

        // Checa destino
        achou = 0;
        for (int j = 0; j < count; j++) {
            if (vertices[j] == g->arestas_todas[i].destino) {
                achou = 1;
                break;
            }
        }
        if (!achou) vertices[count++] = g->arestas_todas[i].destino;
    }
    
    g->num_vertices_unicos = count;
    free(vertices);
}


/**
 * Escreve um relatório sumarizado em um arquivo de texto.
 */
void escreverRelatorio(const Grafo *g, const char *nome_arquivo_saida) {
    FILE *out = fopen(nome_arquivo_saida, "w");
    if (out == NULL) {
        perror("Erro ao criar o arquivo de relatório");
        return;
    }

    fprintf(out, "========================================\n");
    fprintf(out, "      RELATÓRIO DE ANÁLISE DO GRAFO\n");
    fprintf(out, "========================================\n\n");

    fprintf(out, "SUMÁRIO GERAL:\n");
    fprintf(out, "-----------------\n");
    fprintf(out, "Número Total de Vértices Únicos: %d\n", g->num_vertices_unicos);
    fprintf(out, "Número Total de Arestas (linhas lidas): %d\n", g->num_arestas_todas);
    fprintf(out, "Número de Caminhos/Grupos Identificados: %d\n\n", g->num_caminhos);

    fprintf(out, "========================================\n");
    fprintf(out, "      CAMINHOS PRÉ-DEFINIDOS (GRUPOS)\n");
    fprintf(out, "========================================\n\n");

    for (int i = 0; i < g->num_caminhos; i++) {
        fprintf(out, "CAMINHO: %s (Total de %d arestas)\n", g->caminhos[i].nome, g->caminhos[i].num_arestas);
        fprintf(out, "--------------------------------------------------\n");
        for (int j = 0; j < g->caminhos[i].num_arestas; j++) {
            fprintf(out, "  Aresta: %d -> %d\n", g->caminhos[i].arestas[j].origem, g->caminhos[i].arestas[j].destino);
        }
        fprintf(out, "\n");
    }

    fclose(out);
}


/**
 * Libera toda a memória alocada dinamicamente.
 */
void liberarMemoria(Grafo *g) {
    // Libera a memória de cada caminho
    for (int i = 0; i < g->num_caminhos; i++) {
        free(g->caminhos[i].nome);
        free(g->caminhos[i].arestas);
    }
    // Libera o array de caminhos
    free(g->caminhos);
    // Libera o array geral de arestas
    free(g->arestas_todas);
}