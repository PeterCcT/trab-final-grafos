from models.graph.graph_components.edge import Edge
from models.graph.graph_components.vertex import Vertex
from models.graph.graph_representations.graph_representation import GraphRepresentation
from models.graph.graph_representations.graph_representations_types import GraphRepresentationType


class IncidenceRepresentation(GraphRepresentation):
    def __init__(self, quantity_of_vertices: int):
        super().__init__(representation_type=GraphRepresentationType.INCIDENCE, quantity_of_vertices=quantity_of_vertices)
        self.__vertex_edge_incidence: dict[Vertex, set[Edge]] = {vertex: set() for vertex in range(quantity_of_vertices)}
        self.__edge_count = 0
    
    def create_edge(self, vertex_a: Vertex, vertex_b: Vertex):
        edge = (vertex_a, vertex_b)
        self.__vertex_edge_incidence[vertex_a].add(edge)
        self.__vertex_edge_incidence[vertex_b].add(edge)
        self.__edge_count += 1
    
    def delete_edge(self, vertex_a: Vertex, vertex_b: Vertex):
        edge = (vertex_a, vertex_b)
        inverted_edge = (vertex_b, vertex_a)
        if edge in self.__vertex_edge_incidence[vertex_a]:
            self.__vertex_edge_incidence[vertex_a].remove(edge)
        if inverted_edge in self.__vertex_edge_incidence[vertex_a]:
            self.__vertex_edge_incidence[vertex_a].remove(inverted_edge)
        if edge in self.__vertex_edge_incidence[vertex_b]:
            self.__vertex_edge_incidence[vertex_b].remove(edge)
        if inverted_edge in self.__vertex_edge_incidence[vertex_b]:
            self.__vertex_edge_incidence[vertex_b].remove(inverted_edge)
        self.__edge_count -= 1
    
    def is_adjacent_vertex(self, vertex_a: Vertex, vertex_b: Vertex) -> bool:
        for edge in self.__vertex_edge_incidence[vertex_a]:
            v1, v2 = edge
            if v1 == vertex_b or v2 == vertex_b:
                return True
        return False
    
    def is_adjacent_edges(self, edge_a: Edge, edge_b: Edge) -> bool:
        inverted_edge_a = (edge_a[1], edge_a[0])
        inverted_edge_b = (edge_b[1], edge_b[0])
        for vertex in self.__vertex_edge_incidence:
            if (edge_a in self.__vertex_edge_incidence[vertex] and edge_b in self.__vertex_edge_incidence[vertex]) or \
               (inverted_edge_a in self.__vertex_edge_incidence[vertex] and inverted_edge_b in self.__vertex_edge_incidence[vertex]):
                return True
        return False
    
    def is_edge_incidencing_in_vertex(self, edge: Edge, vertex: Vertex) -> bool:
        inverted_edge = (edge[1], edge[0])
        vertex_edges = self.__vertex_edge_incidence.get(vertex, set())
        return edge in vertex_edges or inverted_edge in vertex_edges

    def edge_exists(self, edge: Edge) -> bool:
        inverted_edge = (edge[1], edge[0])
        for edge_vertices in self.__vertex_edge_incidence.values():
            if edge_vertices == edge or edge_vertices == inverted_edge:
                return True
        return False
    
    def get_quantity_of_edges(self) -> int:
        return self.__edge_count

    def get_edges(self) -> set[Edge]:
        edges = set()
        for vertex, incident_edges in self.__vertex_edge_incidence.items():
            for edge in incident_edges:
                v1, v2 = edge
                edges.add((v1, v2))
        return edges

    def is_empty(self) -> bool:
        return self.__edge_count == 0
    
    def is_complete_graph(self) -> bool:
        total_edges = self.quantity_of_vertices * (self.quantity_of_vertices - 1) // 2
        return self.__edge_count == total_edges
    
    def get_incident_edges(self, vertex: Vertex) -> set[int]:
        return self.__vertex_edge_incidence[vertex]