from enum import Enum


class GraphRepresentationType(Enum):
    INCIDENCE = "incidence"
    ADJACENCY_MATRIX = "adjacency_matrix"
    ADJACENCY_LIST = "adjacency_list"