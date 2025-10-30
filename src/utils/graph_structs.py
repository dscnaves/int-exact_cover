from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Aresta:
    origem: int
    destino: int

@dataclass
class Grafo:
    num_vertices: int
    num_arestas: int
    arestas: List[Aresta]

@dataclass
class CaminhosGrupo:
    grupo_id: str
    caminhos: List[List[Tuple[int, int]]]