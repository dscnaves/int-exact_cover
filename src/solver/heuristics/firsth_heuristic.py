def greedyCovergeAlgorithm(graph, paths, k):
    """
    Greedy Algorithm of Covering by Subpaths 

    Args:
        graph: tuple
            tuple (V,E), where
            V = Vertices Set
            E = Egdes Set, each egde e is represent by a tuple (u,v)
        paths: list
            Paths list, each path is a set of egdes 
            ex.: [(u1,v1), (u2,v2), ...]
        k: int
            Max capacity of egdes in a path

    Returns:
        ch_subpaths: list
        Chosen Subpaths list that cover all the egdes exactly once
    """

    V, E = graph
    not_cover_egdes = set(E) # Set of egdes that still need to be covered
    ch_subpaths = []    # Chosen Subpaths list that cover all the egdes exactly once

    # While there are not cover egdes
    while not_cover_egdes:
        best_subpath = []
        best_coverge = 0

        # At each step, find the best subpath (respecting the limite K) composed entirely of egdes not yet corvered
        for s in paths:
            size_p = len(paths)     # Size of the list of paths

            # Variable i represent the beginer of the subpath inside of one of the paths
            for i in range(size_p):
                # Variable j represent the end of the subpath
                # We'll built all the subpaths startting in i and max size of k
                for j in range(i+1, min(i+1+k, size_p)):
                    