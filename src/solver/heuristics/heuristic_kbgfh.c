// heuristic_kbgfh.c
// Compile: gcc -O2 -std=c11 -o bin/heuristic_kbgfh src/solver/heuristics/heuristic_kbgfh.c
// Usage: ./bin/heuristic_kbgfh [input_file] k 
// ./bin/heuristic_kbgfh results/py_parsed_data/teste_dani_c_data.txt 3

// Default input_file: int-exact_cover/results/py_parsed_data/teste_dani_c_data.txt
// Example: ./heuristic_kbgfh int-exact_cover/results/py_parsed_data/teste_dani_c_data.txt 3
// ./bin/heuristic_kbgfh results/py_parsed_data/edges_to_ports_202202100000.anon_c_data.txt 25


#include <stdio.h>      // file I/O (fopen, fgets, printf)
#include <stdlib.h>     // malloc, realloc, free, exit
#include <string.h>     // strcpy, strtok, strlen, strcmp
#include <time.h>       // measuring runtime and timestamp for output filenames

#define MAX_LINE 4096

typedef struct Node_t {
    struct Node_t * prev;
    struct Node_t * next;
    int vertex;
} Node;

typedef struct {
    int vi;      // Initial vertex
    int vf;
    int covered; // 0/1
} Edge;

typedef struct {
    Edge * edges;
    int edge_stored;        // number of egdes read/stored
    int edge_capacity;      // size of the allocated memory
} ArrayEdges;

typedef struct {
    int id;
    Node * head;
    Node * tail;
    int length;
} Path;

typedef struct {
    Path * paths;
    int path_stored;        // number of paths read/stored
    int path_capacity;      // size of the allocated memory
} ArrayPaths;

typedef struct {
    char instance_name[256];
    int total_vertices;
    int total_edges;
    int total_paths;
    ArrayEdges arrayEdges;
    ArrayPaths arrayPaths;      // Paths Pre Selected
} DataSet;


// --- Helper Functions ---

// Convenience function to exit with an error
void die(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(EXIT_FAILURE);
}

// Create and Initialize Node
Node * create_node(int vertex){
    Node * n;
    n = malloc(sizeof(Node));
    if (!n) die("Memory allocation failed for Node");
    n->next = NULL;
    n->prev = NULL;
    n->vertex = vertex;
    return n;
}

ArrayPaths * init_ArrayPaths(){
    ArrayPaths * ap;
    ap->path_capacity = 64;
}

// Initialize DataSet
DataSet * init_dataset(){
    DataSet * ds;
    ds = malloc(sizeof(DataSet));
    if (!ds) die("Memory allocation failed for DataSet");
    
    // Initialize edges array
    ds->arrayEdges.edge_capacity = 64;
    ds->arrayEdges.edge_stored = 0;
    ds->arrayEdges.edges = malloc(ds->arrayEdges.edge_capacity * sizeof(Edge));
    
    // Initialize paths array
    ds->arrayPaths.path_capacity = 64;
    ds->arrayPaths.path_stored = 0;
    ds->arrayPaths.paths = malloc(ds->arrayPaths.path_capacity * sizeof(Path));

    if (!ds->arrayEdges.edges || !ds->arrayPaths.paths) die("Memory allocation failed for arrays");
    return ds;
}

// Function responsible for Dynamic Memory Management
void ensure_edges_capacity(DataSet *ds) {
    // Uninitialized
    if (ds->arrayEdges.edge_capacity == 0) {
        ds->arrayEdges.edge_capacity = 64;
        ds->arrayEdges.edges = malloc(ds->arrayEdges.edge_capacity * sizeof(Edge));
    } 
    // Checks if the array is full
    else if (ds->arrayEdges.edge_stored >= ds->arrayEdges.edge_capacity) {
        ds->arrayEdges.edge_capacity *= 2;
        ds->arrayEdges.edges = realloc(ds->arrayEdges.edges, ds->arrayEdges.edge_capacity * sizeof(Edge));
        if (!ds->arrayEdges.edges) die("Realloc failed for edges");
    }
}

void ensure_arrayPaths_capacity(ArrayPaths * ap) {
    if (ap->path_capacity == 0) {
        ap->path_capacity = 64;
        ap->paths = malloc(ap->path_capacity * sizeof(Path));
    } else if (ap->path_stored >= ap->path_capacity) {
        ap->path_capacity *= 2;
        ap->paths = realloc(ap->paths, ap->path_capacity * sizeof(Path));
        if (!ap->paths) die("Realloc failed for paths");
    }
}

int ** init_coverageEdge(DataSet * ds){
    int ** cover = malloc(ds->total_edges*sizeof(int));
    for (int i = 0; i<ds->total_edges; i++){
        cover[i] = malloc(ds->total_edges*sizeof(int));
    }
    return cover;
}

// Initialize Coverage Matrix (Fixed size logic)
// We use (total_vertices + 1) to handle 1-based indexing safely
int ** init_coverageMatrix(int total_vertices){
    int ** cover = malloc((total_vertices + 1) * sizeof(int*));
    for (int i = 0; i <= total_vertices; i++){
        cover[i] = calloc((total_vertices + 1), sizeof(int)); // calloc initializes to 0
    }
    return cover;
}

// --- Parsing ---
void parse_input_file(const char *filename, DataSet *ds){
    FILE * f = fopen(filename,"r");
    if (!f) {
        char tmp[512];
        snprintf(tmp, sizeof(tmp), "Could not open input file: %s", filename);
        die(tmp);
    }
    char line[MAX_LINE];
    while (fgets(line, sizeof(line), f)) {
        // strip newline
        size_t L = strlen(line);

        // "Hello\n\0" -> "Hello\0\0"
        while (L && (line[L-1]=='\n' || line[L-1]=='\r')) { line[--L] = 0; }
        if (L == 0) continue;
        if (line[0] == '#') continue;

        // header lines: KEY:VALUE
        if (strncmp(line, "INSTANCE_NAME:", 14) == 0) {
            const char *val = line + 14;
            while (*val == ' ' || *val == '\t') val++;
            strncpy(ds->instance_name, val, sizeof(ds->instance_name)-1);
            ds->instance_name[sizeof(ds->instance_name)-1] = 0;
            continue;
        }
        if (strncmp(line, "TOTAL_VERTICES:", 15) == 0) {
            ds->total_vertices = atoi(line + 15);
            continue;
        }
        if (strncmp(line, "TOTAL_EDGES:", 12) == 0) {
            ds->total_edges = atoi(line + 12);
            continue;
        }
        if (strncmp(line, "TOTAL_PATHS:", 12) == 0) {
            ds->total_paths = atoi(line + 12);
            continue;
        }

        // path lines: ID;NUM_VERTICES;V1,V2,V3,...
        char *p = line;
        // skip leading spaces
        while (*p == ' ' || *p == '\t') p++;
        
        // 1. Path ID
        char *tok = strtok(p, ";");
        if (!tok) continue;
        int path_id = atoi(tok);

        // 2. Num Vertices
        tok = strtok(NULL, ";");
        if (!tok) continue;
        int num_vertices = atoi(tok);

        // 3. Vertices List
        tok = strtok(NULL, ";");
        if (!tok) continue;

        // Ensure capacity
        ensure_arrayPaths_capacity(&ds->arrayPaths);

        // Get pointer to the current path slot
        int p_idx = ds->arrayPaths.path_stored;
        Path *current_path = &ds->arrayPaths.paths[p_idx];

        current_path->id = path_id;
        current_path->length = num_vertices;
        current_path->head = NULL;
        current_path->tail = NULL;

        // Now tok is "V1,V2,..." parse integers
        // Parse vertices separated by commas within the last token
        // Note: The previous strtok ended at ';'. We need to tokenize 'tok' now by ','
        // However, standard strtok maintains internal state. We must use 'tok' as the new string.
        char *vcur = strtok(tok, ",");
        int count = 0;

        while (vcur != NULL) {
            int vertex = atoi(vcur);
            Node *new_node = create_node(atoi(vcur));
            
            if (current_path->head == NULL) {
                // First node
                current_path->head = new_node;
                current_path->tail = new_node;
            } else {
                // Append to tail
                new_node->prev = current_path->tail;
                current_path->tail->next = new_node;
                current_path->tail = new_node;
            }
            count++;
            vcur= strtok(NULL, ",");
        }

        if (count != num_vertices) {
            fprintf(stderr, "Warning: Declared %d vertices but found %d for path %d\n", num_vertices, count, path_id);
        }

        ds->arrayPaths.path_stored++;
    }
    fclose(f);
}

// Clean up memory
void free_dataset(DataSet *ds) {
    if (!ds) return;

    // Free Edges
    if (ds->arrayEdges.edges) free(ds->arrayEdges.edges);

    // Free Paths (and their linked lists)
    if (ds->arrayPaths.paths) {
        for (int i = 0; i < ds->arrayPaths.path_stored; i++) {
            Node *curr = ds->arrayPaths.paths[i].head;
            while (curr) {
                Node *tmp = curr;
                curr = curr->next;
                free(tmp);
            }
        }
        free(ds->arrayPaths.paths);
    }

    free(ds);
}

void free_coverageMatrix(int ** matrix, int total_vertices) {
    for (int i = 0; i <= total_vertices; i++) {
        free(matrix[i]);
    }
    free(matrix);
}

void free_solutions(ArrayPaths *ap) {
    if (!ap) return;

    // 1. Check if the paths array exists
    if (ap->paths) {
        // Iterate over each stored path
        for (int i = 0; i < ap->path_stored; i++) {
            Node *curr = ap->paths[i].head;
            
            // 2. Free the linked list (Nodes) of this path
            while (curr != NULL) {
                Node *temp = curr;     // Save the current node
                curr = curr->next;     // Move to the next node
                free(temp);            // Free the current node
            }
        }
        // 3. Free the array holding the Path structs
        free(ap->paths);
    }

    // 4. Free the main structure pointer
    free(ap);
}

// int fragmentation(int k, DataSet * ds, int ** coverageMatrix, ArrayPaths * chosenPaths, int num_coverEdges){
    
//     // First choise of path
//     Path pcur = ds->arrayPaths.paths[0];
//     if (pcur.length <= k){
//         chosenPaths->path_stored++;
//         ensure_arrayPaths_capacity(chosenPaths);
//         chosenPaths->paths[0] = pcur;

//         Node * nodeCur = pcur.head;
//         for(int i = 0; i<pcur.length-1; i++){
//             int vi = nodeCur->vertex;
//             nodeCur = nodeCur->next;
//             int vf = nodeCur->vertex;
//             coverageMatrix[vi][vf] = 1;
//             num_coverEdges++;
//         }
//     } else {
//         Node * nodeCur = pcur.head;
//         for(int i = 0; i<k; i++){
//             chosenPaths->path_stored++;
//             ensure_arrayPaths_capacity(chosenPaths);
        
//             chosenPaths->paths[0].head = nodeCur;

//             int vi = nodeCur->vertex;
//             nodeCur = nodeCur->next;
//             int vf = nodeCur->vertex;
//             coverageMatrix[vi][vf] = 1;
//             num_coverEdges++;
//         }
//     }
//     int path_idx = 1;
//     // Chosing the paths from the second one onwards
//     while(num_coverEdges != ds->total_edges){
//         pcur = ds->arrayPaths.paths[path_idx];

//         // Util variable: At least one vertex of the path was add? 1:0
//         int util = 0;

//         // Vertex Iteration
//         Node * nodeCur = pcur.head;
//         for(int i = 0; i<k; i++){
//             int vi = nodeCur->vertex;
//             nodeCur = nodeCur->next;
//             int vf = nodeCur->vertex;
//             if (coverageMatrix[vi][vf] == 0){
//                 if (util==0){
//                     chosenPaths->path_stored++;
//                     ensure_arrayPaths_capacity(chosenPaths);
//                     util++;
//                 }
//                 coverageMatrix[vi][vf] == 1;
//                 num_coverEdges++;
//                 chosenPaths->paths[chosenPaths->path_stored].tail->next = nodeCur->prev;
//                 chosenPaths->paths[chosenPaths->path_stored].tail
//             } else{
//                 chosenPaths->path_stored++;
//                 ensure_arrayPaths_capacity(chosenPaths);
//                 nodeCur = nodeCur->next;
//             }           
//         }
        

//         path_idx++;
//     }

// }

void write_solution(const char *directory, DataSet *ds, ArrayPaths *solution, double time_taken, int k) {
    char filepath[512];
    
    // Constrói o caminho: results/heuristic/NOME_INSTANCIA_KBGFH_k3.txt
    snprintf(filepath, sizeof(filepath), "%s/%s_KBGFH_k%d.txt", directory, ds->instance_name, k);
    
    FILE *f = fopen(filepath, "w");
    if (!f) { 
        fprintf(stderr, "Warning: Could not write to %s. Check if directory exists.\n", filepath); 
        return; 
    }

    // Calcular o total de arestas únicas cobertas (Soma de edges de cada subpath)
    int total_edges_covered = 0;
    for(int i = 0; i < solution->path_stored; i++) {
        // Num arestas = Num vértices (length) - 1
        if (solution->paths[i].length > 0)
            total_edges_covered += (solution->paths[i].length - 1);
    }

    // Header conforme solicitado
    fprintf(f, "INSTANCE_NAME:%s\n", ds->instance_name);
    fprintf(f, "HEURISTIC:K-Bounded Greedy Fragmentation Heuristic (K-BGFH)\n");
    fprintf(f, "K:%d\n", k);
    fprintf(f, "SELECTED_SUBPATHS:%d\n", solution->path_stored);
    fprintf(f, "RUN_TIME_SECONDS:%.6f\n", time_taken);
    fprintf(f, "TOTAL_UNIQUE_EDGES:%d\n", total_edges_covered);
    fprintf(f, "\n");
    fprintf(f, "# SELECTED FRAGMENTS (path_id;start_edge_index;num_edges;vertex_sequence)\n");
    
    // Lista de fragmentos
    for(int i = 0; i < solution->path_stored; i++) {
        Path *p = &solution->paths[i];
        int num_edges = p->length - 1;
        
        // start_edge_index está fixo em 0 pois a struct atual não guarda o offset original.
        fprintf(f, "%d;0;%d;", p->id, num_edges);
        
        Node *curr = p->head;
        while(curr) {
            fprintf(f, "%d", curr->vertex);
            if(curr->next) fprintf(f, "->");
            curr = curr->next;
        }
        fprintf(f, "\n");
    }
    
    fclose(f);
    printf("Results written to: %s\n", filepath);
}

// --- Core Function of the Heuristic ---

// Auxiliary function to save the current fragment in the array of chosen fragments and reset the temporary struct
void save_and_reset_fragment(Path *frag, ArrayPaths *chosenPaths) {
    
    // Only save if there is at least 1 edge (i.e., >= 2 vertices)
    if (frag->head != NULL && frag->length >= 2) {
        ensure_arrayPaths_capacity(chosenPaths);
        frag->id = chosenPaths->path_stored;
        chosenPaths->paths[chosenPaths->path_stored] = *frag; // Copy struct
        chosenPaths->path_stored++;
    } else {
        // If it is an orphan node (e.g., isolated vertex), free memory
        if (frag->head) free(frag->head);
    }
    // Reset fragment
    frag->head = NULL;
    frag->tail = NULL;
    frag->length = 0;
    // Increment ID for the next one
    frag->id++; 
}

void fragmentation(int k, DataSet * ds, int ** coverageMatrix, ArrayPaths * chosenPaths) {
    
    // Iterate over all input paths
    for (int i = 0; i < ds->arrayPaths.path_stored; i++) {
        
        Path * originalPath = &ds->arrayPaths.paths[i];
        Node * currNode = originalPath->head;
        
        // Temporary fragment being built
        Path currentFragment;
        currentFragment.id = chosenPaths->path_stored;
        currentFragment.length = 0; 
        currentFragment.head = NULL;
        currentFragment.tail = NULL;

        // Traverse vertices of the original path: u -> v
        while (currNode != NULL && currNode->next != NULL) {
            int u = currNode->vertex;
            int v = currNode->next->vertex;

            // Check if edge (u, v) is already covered
            // Adjust here if the graph is undirected: (matrix[u][v] || matrix[v][u])
            if (u < 0 || u > ds->total_vertices || v < 0 || v > ds->total_vertices) {
                fprintf(stderr, "Índice de vértice inválido: (%d, %d)\n", u, v);
                currNode = currNode->next;
                continue;
            }
            int is_covered = (coverageMatrix[u][v] == 1); 

            if (!is_covered) {
                // --- Edge NOT Covered ---
                
                // 1. Mark as covered
                coverageMatrix[u][v] = 1;
                // coverageMatrix[v][u] = 1; // Adjust here if the graph is undirected

                // 2. If fragment is empty, start with 'u'
                if (currentFragment.head == NULL) {
                    Node * n = create_node(u);
                    currentFragment.head = n;
                    currentFragment.tail = n;
                    currentFragment.length = 1; 
                }

                // 3. Add 'v' to the fragment
                Node * n = create_node(v);
                n->prev = currentFragment.tail;
                currentFragment.tail->next = n;
                currentFragment.tail = n;
                currentFragment.length++;

                // 4. K Limit Check
                // path.length counts vertices. k is edges.
                // Ex: k=3 edges requires 4 vertices.
                if (currentFragment.length == (k + 1)) {
                    // We reached size k.
                    // Save this piece.
                    ensure_arrayPaths_capacity(chosenPaths);    ///
                    currentFragment.id = chosenPaths->path_stored;
                    chosenPaths->paths[chosenPaths->path_stored] = currentFragment;
                    chosenPaths->path_stored++;

                    // START OF NEXT FRAGMENT (Overlap on vertex)
                    // Since the cut was by SIZE (and not by covered edge),
                    // the next subpath MUST start at 'v' to continue covering the next edges.
                    
                    // Manually reset to keep vertex 'v'
                    currentFragment.id++;
                    Node * startNode = create_node(v); // The current 'v' becomes the 'u' of the next one
                    currentFragment.head = startNode;
                    currentFragment.tail = startNode;
                    currentFragment.length = 1;
                }

            } else {
                // --- Edge ALREADY Covered (The "Cut") ---
                // We found a gap. The current fragment (if it exists) ends at 'u'.
                // The next fragment (if any) will only start at the next valid edge.
                
                save_and_reset_fragment(&currentFragment, chosenPaths);
                
                // Note: We do not add 'v' to anything right now. 
                // In the next loop iteration, 'currNode' will be 'v', and we will test edge v -> w.
                // If v -> w is valid, a new fragment will start at 'v'.
            }

            // Advance in the original path
            currNode = currNode->next;
        }

        // End of Path Loop: Save what remains in the buffer
        save_and_reset_fragment(&currentFragment, chosenPaths);
    }
}




// --- Main ---

int main(int argc, char **argv){

    const char *default_input = "int-exact_cover/results/py_parsed_data/teste_dani_c_data.txt";
    const char *input_file = (argc >= 2) ? argv[1] : default_input;
    if (argc < 3) {
        fprintf(stderr, "Usage: %s [input_file] k\nDefault input_file: %s\n", argv[0], default_input);
        // continue if arguable, but require k
    }
    if (argc < 3) die("Please provide k (max edges per fragment) as 2nd argument.");

    int k = atoi(argv[2]);
    if (k <= 0) die("k must be > 0");

    // 1. Initialization
    DataSet *ds = init_dataset();

    // 2. Parse
    parse_input_file(input_file, ds);

    // Output stats to verify
    printf("Instance: %s\n", ds->instance_name);
    printf("Vertices: %d, Edges: %d, Paths Loaded: %d\n", 
           ds->total_vertices, ds->total_edges, ds->arrayPaths.path_stored);

    // Verify Linked List of the first path (if exists)
    if (ds->arrayPaths.path_stored > 0) {
        printf("First Path Nodes: ");
        Node *curr = ds->arrayPaths.paths[0].head;
        while(curr) {
            printf("%d -> ", curr->vertex);
            curr = curr->next;
        }
        printf("NULL\n");
    }

    // 3. Prepare Structures
    int ** coverageMatrix = init_coverageMatrix(ds->total_vertices);
    ArrayPaths * chosenPaths = malloc(sizeof(ArrayPaths));
    chosenPaths->path_capacity = 0;
    chosenPaths->path_stored = 0;
    chosenPaths->paths = NULL; 

    // 4. Run Heuristic
    // Logic for kbgfh heuristic
    clock_t start = clock();
    
    fragmentation(k, ds, coverageMatrix, chosenPaths);
    
    clock_t end = clock();
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;

    printf("Heuristic Completed. Subpaths chosen: %d\n", chosenPaths->path_stored);

    // 5. Write Results
    write_solution("int-exact_cover/results/heuristic", ds, chosenPaths, time_taken, k);

    // 6. Cleanup
    free_coverageMatrix(coverageMatrix, ds->total_vertices);
    free_dataset(ds);
    free_solutions(chosenPaths);    // Releases the solution found (output)

    return 0;
}