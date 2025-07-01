from models.graph.graph_components.edge import Edge
from models.graph.graph_components.vertex import Vertex
from models.graph.graph_representations.graph_representation import GraphRepresentation
from models.graph.graph_representations.graph_representations_types import GraphRepresentationType


class AdjacencyListRepresentation(GraphRepresentation):
    def __init__(self, quantity_of_vertices: int):
        super().__init__(GraphRepresentationType.ADJACENCY_MATRIX, quantity_of_vertices)
        self.__adjacency_lists: list[set[Vertex]] = [set() for _ in range(quantity_of_vertices)]
        self.__quantity_of_edges = 0

    def create_edge(self, vertex_a: Vertex, vertex_b: Vertex) -> None:
        if vertex_b not in self.__adjacency_lists[vertex_a]:
            self.__adjacency_lists[vertex_a].add(vertex_b)
        if vertex_a not in self.__adjacency_lists[vertex_b]:
            self.__adjacency_lists[vertex_b].add(vertex_a)
        self.__quantity_of_edges += 1

    def delete_edge(self, vertex_a: Vertex, vertex_b: Vertex) -> None:
        if vertex_b in self.__adjacency_lists[vertex_a]:
            self.__adjacency_lists[vertex_a].remove(vertex_b)
        if vertex_a in self.__adjacency_lists[vertex_b]:
            self.__adjacency_lists[vertex_b].remove(vertex_a)
        self.__quantity_of_edges -= 1
    
    def is_adjacent_vertex(self, vertex_a: Vertex, vertex_b: Vertex) -> bool:
        return vertex_b in self.__adjacency_lists[vertex_a]

    def is_adjacent_edges(self, edge_a: tuple[Vertex, Vertex], edge_b: tuple[Vertex, Vertex]) -> bool:
        for vertex_a in edge_a:
            for vertex_b in edge_b:
                if self.is_adjacent_vertex(vertex_a, vertex_b):
                    return True
        return False

    def is_edge_incidencing_in_vertex(self, edge: tuple[Vertex, Vertex], vertex: Vertex) -> bool:
        return self.is_adjacent_vertex(edge[0], vertex) or self.is_adjacent_vertex(edge[1], vertex)

    def edge_exists(self, edge: tuple[Vertex, Vertex]) -> bool:
        return self.is_adjacent_vertex(edge[0], edge[1])

    def get_quantity_of_edges(self) -> int:
        return self.__quantity_of_edges

    def is_empty(self) -> bool:
        return all(len(adjacency_list) == 0 for adjacency_list in self.__adjacency_lists)

    def is_complete_graph(self) -> bool:
        total_edges = self.quantity_of_vertices * (self.quantity_of_vertices - 1) // 2
        quantity_of_edges = self.get_quantity_of_edges()
        return quantity_of_edges == total_edges

    def get_edges(self) -> set[Edge]:
        edges = set()
        for vertex, adjacents in enumerate(self.__adjacency_lists):
            for adjacent in adjacents:
                edges.add((vertex, adjacent))
        return edges
