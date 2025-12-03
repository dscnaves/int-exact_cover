// heuristic_kbgfh.c
// Compile: gcc -O2 -std=c11 -o bin/heuristic_kbgfh src/solver/heuristics/heuristic_kbgfh.c
// Usage: ./bin/heuristic_kbgfh [input_file] k 
// ./bin/heuristic_kbgfh results/py_parsed_data/teste_dani_c_data.txt 3

// Default input_file: int-exact_cover/results/py_parsed_data/teste_dani_c_data.txt
// Example: ./heuristic_kbgfh int-exact_cover/results/py_parsed_data/teste_dani_c_data.txt 3


#include <stdio.h>      // file I/O (fopen, fgets, printf)
#include <stdlib.h>     // malloc, realloc, free, exit
#include <string.h>     // strcpy, strtok, strlen, strcmp
#include <time.h>       // measuring runtime and timestamp for output filenames

#define MAX_LINE 4096   

typedef struct {
    int u, v;
    int id;
    int covered; // 0/1
} Edge;

typedef struct {
    int id;                 // path ID
    int num_vertices;
    int *vertices;          // vertex list length = num_vertices  -  [v1, v2, v3, …]
    int num_edges;          // num_vertices - 1
    int *edge_ids;          // length = num_edges -> indices into global edges array
} Path;

typedef struct {
    char instance_name[256];
    int total_vertices;
    int total_edges_declared;
    int total_paths_declared;
    Edge *edges;
    int edges_count;        // number of egdes sotred in the array of Egdes
    int edges_capacity;
    Path *paths;
    int paths_count;        // number of egdes sotred in the array of Paths
    int paths_capacity;
} DataSet;

// Convenience function to exit with an error
void die(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(EXIT_FAILURE);
}

void ensure_edges_capacity(DataSet *ds) {
    if (ds->edges_capacity == 0) {
        ds->edges_capacity = 64;
        ds->edges = malloc(ds->edges_capacity * sizeof(Edge));
    } else if (ds->edges_count >= ds->edges_capacity) {
        ds->edges_capacity *= 2;
        ds->edges = realloc(ds->edges, ds->edges_capacity * sizeof(Edge));
    }
}

void ensure_paths_capacity(DataSet *ds) {
    if (ds->paths_capacity == 0) {
        ds->paths_capacity = 64;
        ds->paths = malloc(ds->paths_capacity * sizeof(Path));
    } else if (ds->paths_count >= ds->paths_capacity) {
        ds->paths_capacity *= 2;
        ds->paths = realloc(ds->paths, ds->paths_capacity * sizeof(Path));
    }
}

// linear search for edge (u,v). If not found and create_if_missing==1, add it.
int find_or_add_edge(DataSet *ds, int u, int v, int create_if_missing) {
    for (int i = 0; i < ds->edges_count; ++i) {
        if (ds->edges[i].u == u && ds->edges[i].v == v) return ds->edges[i].id;
    }
    if (!create_if_missing) return -1;
    ensure_edges_capacity(ds);
    int id = ds->edges_count;
    ds->edges[id].u = u;
    ds->edges[id].v = v;
    ds->edges[id].id = id;
    ds->edges[id].covered = 0;
    ds->edges_count++;
    return id;
}

void free_dataset(DataSet *ds) {
    for (int i = 0; i < ds->paths_count; ++i) {
        free(ds->paths[i].vertices);
        free(ds->paths[i].edge_ids);
    }
    free(ds->paths);
    free(ds->edges);
}

void parse_input_file(const char *filename, DataSet *ds) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        char tmp[512];
        snprintf(tmp, sizeof(tmp), "Could not open input file: %s", filename);
        die(tmp);
    }
    char line[MAX_LINE];
    while (fgets(line, sizeof(line), f)) {
        // strip newline
        size_t L = strlen(line);
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
            ds->total_edges_declared = atoi(line + 12);
            continue;
        }
        if (strncmp(line, "TOTAL_PATHS:", 12) == 0) {
            ds->total_paths_declared = atoi(line + 12);
            continue;
        }

        // path lines: ID;NUM_VERTICES;V1,V2,V3,...
        char *p = line;
        // skip leading spaces
        while (*p == ' ' || *p == '\t') p++;
        // parse id
        char *tok = strtok(p, ";");
        if (!tok) continue;
        int path_id = atoi(tok);

        tok = strtok(NULL, ";");
        if (!tok) continue;
        int num_vertices = atoi(tok);

        tok = strtok(NULL, ";");
        if (!tok) continue;
        // now tok is "V1,V2,..." parse integers
        int *verts = malloc(sizeof(int) * num_vertices);
        int idx = 0;
        char *vcur = strtok(tok, ",");
        while (vcur != NULL && idx < num_vertices) {
            verts[idx++] = atoi(vcur);
            vcur = strtok(NULL, ",");
        }
        if (idx != num_vertices) {
            free(verts);
            die("Mismatch between declared and parsed number of vertices in a path.");
        }

        // create path struct
        ensure_paths_capacity(ds);
        Path *path = &ds->paths[ds->paths_count];
        path->id = path_id;
        path->num_vertices = num_vertices;
        path->vertices = verts;
        path->num_edges = (num_vertices >= 1) ? (num_vertices - 1) : 0;
        path->edge_ids = NULL;
        if (path->num_edges > 0) {
            path->edge_ids = malloc(sizeof(int) * path->num_edges);
            for (int i = 0; i < path->num_edges; ++i) {
                int u = verts[i];
                int v = verts[i+1];
                int eid = find_or_add_edge(ds, u, v, 1);
                path->edge_ids[i] = eid;
            }
        }
        ds->paths_count++;
    }
    fclose(f);
}

// Mark all edges as uncovered initially
void init_coverage(DataSet *ds) {
    for (int i = 0; i < ds->edges_count; ++i) ds->edges[i].covered = 0;
}

// Utility to produce fragment vertex sequence string
char *fragment_vertices_string(Path *p, int start_edge_idx, int len_edges) {
    // fragment covers edges start_edge_idx .. start_edge_idx+len_edges-1
    // vertices from start vertex = vertices[start_edge_idx] to vertices[start_edge_idx + len_edges]
    int vlen = len_edges + 1;
    int start_v = start_edge_idx;
    int tot = vlen * 8 + 32;
    char *s = malloc(tot);
    s[0] = 0;
    for (int i = 0; i < vlen; ++i) {
        char tmp[32];
        snprintf(tmp, sizeof(tmp), "%d", p->vertices[start_v + i]);
        strcat(s, tmp);
        if (i+1 < vlen) strcat(s, "->");
    }
    return s;
}

int count_uncovered_in_fragment(DataSet *ds, Path *p, int start_edge_idx, int len_edges) {
    int cnt = 0;
    for (int i = 0; i < len_edges; ++i) {
        int eid = p->edge_ids[start_edge_idx + i];
        if (!ds->edges[eid].covered) cnt++;
    }
    return cnt;
}

int all_edges_covered(DataSet *ds) {
    for (int i = 0; i < ds->edges_count; ++i)
        if (!ds->edges[i].covered) return 0;
    return 1;
}

int main(int argc, char **argv) {
    const char *default_input = "int-exact_cover/results/py_parsed_data/teste_dani_c_data.txt";
    const char *input_file = (argc >= 2) ? argv[1] : default_input;
    if (argc < 3) {
        fprintf(stderr, "Usage: %s [input_file] k\nDefault input_file: %s\n", argv[0], default_input);
        // continue if arguable, but require k
    }
    if (argc < 3) die("Please provide k (max edges per fragment) as 2nd argument.");

    int k = atoi(argv[2]);
    if (k <= 0) die("k must be > 0");

    DataSet ds;
    memset(&ds, 0, sizeof(ds));
    parse_input_file(input_file, &ds);

    init_coverage(&ds);

    // prepare results container
    typedef struct {
        int path_id;
        int start_edge_idx;
        int len_edges;
        char *vertices_str;
    } Fragment;
    Fragment *solution = NULL;
    int sol_count = 0, sol_cap = 0;
    #define ENSURE_SOL_CAP() if(sol_cap==0){sol_cap=128;solution=malloc(sol_cap*sizeof(Fragment));} else if(sol_count>=sol_cap){sol_cap*=2;solution=realloc(solution,sol_cap*sizeof(Fragment));}

    clock_t tstart = clock();

    // main greedy loop: while uncovered edges exist, find fragment (any path, any position) with best uncovered count (len <= k)
    while (!all_edges_covered(&ds)) {
        int best_uncovered = 0;
        int best_path_idx = -1;
        int best_start = -1;
        int best_len = 0;

        // scan all paths
        for (int pi = 0; pi < ds.paths_count; ++pi) {
            Path *p = &ds.paths[pi];
            if (p->num_edges <= 0) continue;
            // consider every start position
            for (int s = 0; s < p->num_edges; ++s) {
                // try len 1..k but not exceeding remaining edges
                for (int L = 1; L <= k && s + L <= p->num_edges; ++L) {
                    int cnt_un = count_uncovered_in_fragment(&ds, p, s, L);
                    if (cnt_un > best_uncovered || (cnt_un == best_uncovered && L > best_len)) {
                        best_uncovered = cnt_un;
                        best_path_idx = pi;
                        best_start = s;
                        best_len = L;
                    }
                }
            }
        }

        if (best_uncovered == 0) {
            // No fragment adds new uncovered edges -> we might have isolated uncovered edges that our path fragments can't reach,
            // but this is unlikely because we enumerated all fragments. Break to avoid infinite loop.
            break;
        }

        // select fragment and mark edges covered
        Path *best_path = &ds.paths[best_path_idx];
        ENSURE_SOL_CAP();
        solution[sol_count].path_id = best_path->id;
        solution[sol_count].start_edge_idx = best_start;
        solution[sol_count].len_edges = best_len;
        solution[sol_count].vertices_str = fragment_vertices_string(best_path, best_start, best_len);
        sol_count++;

        for (int i = 0; i < best_len; ++i) {
            int eid = best_path->edge_ids[best_start + i];
            ds.edges[eid].covered = 1;
        }
    }

    clock_t tend = clock();
    double elapsed = (double)(tend - tstart) / CLOCKS_PER_SEC;

    // create output directory if needed
    const char *outdir = "int-exact_cover/results/heuristic";
    char cmd[512];
    // try creating directory (POSIX)
    snprintf(cmd, sizeof(cmd), "mkdir -p %s", outdir);
    system(cmd);

    // Build output filename: INSTANCE_HEUR_res_epoch.txt
    time_t now = time(NULL);
    char outfname[512];
    snprintf(outfname, sizeof(outfname), "%s/%s_K-BGFH_res_%ld.txt", outdir, ds.instance_name, (long)now);

    FILE *fo = fopen(outfname, "w");
    if (!fo) {
        fprintf(stderr, "Failed to open output file '%s' for writing.\n", outfname);
    } else {
        fprintf(fo, "INSTANCE_NAME:%s\n", ds.instance_name);
        fprintf(fo, "HEURISTIC:K-Bounded Greedy Fragmentation Heuristic (K-BGFH)\n");
        fprintf(fo, "K:%d\n", k);
        fprintf(fo, "SELECTED_SUBPATHS:%d\n", sol_count);
        fprintf(fo, "RUN_TIME_SECONDS:%.6f\n", elapsed);
        fprintf(fo, "TOTAL_UNIQUE_EDGES:%d\n", ds.edges_count);
        fprintf(fo, "\n# SELECTED FRAGMENTS (path_id;start_edge_index;num_edges;vertex_sequence)\n");
        for (int i = 0; i < sol_count; ++i) {
            fprintf(fo, "%d;%d;%d;%s\n",
                solution[i].path_id,
                solution[i].start_edge_idx,
                solution[i].len_edges,
                solution[i].vertices_str);
        }
        fclose(fo);
        printf("Wrote results to: %s\n", outfname);
    }

    // also print a brief summary to stdout
    printf("Instance: %s\nHeuristic: K-Bounded Greedy Fragmentation Heuristic (K-BGFH)\n", ds.instance_name);
    printf("Unique edges discovered: %d\n", ds.edges_count);
    printf("Selected fragments: %d\n", sol_count);
    printf("Elapsed (s): %.6f\n", elapsed);

    // cleanup
    for (int i = 0; i < sol_count; ++i) free(solution[i].vertices_str);
    free(solution);
    free_dataset(&ds);
    return 0;
}
