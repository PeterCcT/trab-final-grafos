from enum import StrEnum

from models.graph.graph_components.vertex import Vertex

class EdgeInfoTypes(StrEnum):
    LABEL = "label"
    WEIGHT = "weight"

Edge = tuple[Vertex, Vertex]