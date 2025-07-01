from models.graph.graph_components.edge import Edge
from models.graph.graph_components.vertex import Vertex
from models.graph.graph_representations.graph_representation import GraphRepresentation
from models.graph.graph_representations.graph_representations_types import GraphRepresentationType


class AdjacencyMatrixRepresentation(GraphRepresentation):
    def __init__(self, quantity_of_vertices: int):
        super().__init__(GraphRepresentationType.ADJACENCY_MATRIX, quantity_of_vertices)
        row = [0] * quantity_of_vertices
        self.__adjacency_matrix = [row[:] for _ in range(quantity_of_vertices)]
        self.__quantity_of_edges = 0

    def create_edge(self, vertex_a: Vertex, vertex_b: Vertex) -> None:
        self.__adjacency_matrix[vertex_a][vertex_b] = 1
        self.__adjacency_matrix[vertex_b][vertex_a] = 1
        self.__quantity_of_edges += 1

    def delete_edge(self, vertex_a: Vertex, vertex_b: Vertex) -> None:
        self.__adjacency_matrix[vertex_a][vertex_b] = 0
        self.__adjacency_matrix[vertex_b][vertex_a] = 0
        self.__quantity_of_edges -= 1

    def is_adjacent_vertex(self, vertex_a: Vertex, vertex_b: Vertex) -> bool:
        return self.__adjacency_matrix[vertex_a][vertex_b] == 1

    def is_adjacent_edges(self, edge_a: Edge, edge_b: Edge) -> bool:
        for vertex_a in edge_a:
            for vertex_b in edge_b:
                if self.is_adjacent_vertex(vertex_a, vertex_b):
                    return True
        return False

    def is_edge_incidencing_in_vertex(self, edge: Edge, vertex: Vertex) -> bool:
        return self.is_adjacent_vertex(edge[0], vertex) or self.is_adjacent_vertex(edge[1], vertex)
    
    def edge_exists(self, edge: Edge) -> bool:
        return self.is_adjacent_vertex(edge[0], edge[1])
    
    def get_quantity_of_edges(self) -> int:
        return self.__quantity_of_edges

    def is_empty(self) -> bool:
        for row in self.__adjacency_matrix:
            for value in row:
                if value != 0:
                    return False
        return True

    def is_complete_graph(self) -> bool:
        total_edges = self.quantity_of_vertices * (self.quantity_of_vertices - 1) // 2
        return self.__quantity_of_edges == total_edges
    
    def get_edges(self):
        edges = set()
        for i in range(self.quantity_of_vertices):
            for j in range(i + 1, self.quantity_of_vertices):
                if self.__adjacency_matrix[i][j] == 1:
                    edges.add((i, j))
        return edges