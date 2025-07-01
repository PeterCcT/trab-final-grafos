from typing import Any

from models.graph.graph_components.edge import Edge, EdgeInfoTypes
from models.graph.graph_components.vertex import Vertex, VertexInfoTypes
from models.graph.graph_representations.adjacency.adjacency_matrix_representation import AdjacencyMatrixRepresentation
from models.graph.graph_representations.adjacency.adjacenty_list_representation import AdjacencyListRepresentation
from models.graph.graph_representations.graph_representation import GraphRepresentation
from models.graph.graph_representations.graph_representations_types import GraphRepresentationType
from models.graph.graph_representations.incidence.incidence_representation import IncidenceRepresentation

class Graph:
    def __init__(self, quantity_of_vertices: int, representations: set[GraphRepresentationType] = None):
        self.quantity_of_vertices = quantity_of_vertices
        self.__graph_representations: dict[GraphRepresentationType, GraphRepresentation] = {}

        self.__vertexes_info: dict[Vertex, dict[VertexInfoTypes, Any]] = {}
        self.__edges_info: dict[Edge, dict[EdgeInfoTypes, Any]] = {}
        
        self.__fill_graph_representations(representations)

    def __fill_graph_representations(self, representations: set[GraphRepresentationType] = None):
        if not representations:
            representations = {GraphRepresentationType.ADJACENCY_MATRIX, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.INCIDENCE}
        if GraphRepresentationType.INCIDENCE not in representations:
            representations.add(GraphRepresentationType.INCIDENCE)
        for representation in representations:
            if representation == GraphRepresentationType.ADJACENCY_MATRIX:
                self.__graph_representations[representation] = AdjacencyMatrixRepresentation(self.quantity_of_vertices)
            elif representation == GraphRepresentationType.ADJACENCY_LIST:
                self.__graph_representations[representation] = AdjacencyListRepresentation(self.quantity_of_vertices)
            elif representation == GraphRepresentationType.INCIDENCE:
                self.__graph_representations[representation] = IncidenceRepresentation(self.quantity_of_vertices)


    def create_edge(self, vertex_a: Vertex, vertex_b: Vertex):
        for representation in self.__graph_representations.values():
            representation.create_edge(vertex_a, vertex_b)

    def delete_edge(self, vertex_a: Vertex, vertex_b: Vertex):
        for representation in self.__graph_representations.values():
            representation.delete_edge(vertex_a, vertex_b)

    def add_vertex_info(self, info_type: VertexInfoTypes, vertex: Vertex, value: Any):
        if vertex not in self.__vertexes_info:
            self.__vertexes_info[vertex] = {}
        if info_type == VertexInfoTypes.LABEL and value is None:
            raise ValueError("Label value cannot be None")
        self.__vertexes_info[vertex][info_type] = value
    
    def add_edge_info(self, info_type: EdgeInfoTypes, edge: Edge, value: Any):
        if edge not in self.__edges_info:
            self.__edges_info[edge] = {}
        if info_type == EdgeInfoTypes.LABEL and value is None:
            raise ValueError("Label value cannot be None")
        self.__edges_info[edge][info_type] = value
    
    def get_vertex_info(self, info: VertexInfoTypes, vertex: Vertex) ->  Any:
        return self.__vertexes_info.get(vertex, {}).get(info)

    def get_edge_info(self, info: EdgeInfoTypes, edge: Edge) -> Any:
        return self.__edges_info.get(edge, {}).get(info)

    def __get_first_disponible_representation(self, representations: list[GraphRepresentationType]) -> GraphRepresentation:
        for representation in representations:
            if representation in self.__graph_representations:
                return self.__graph_representations[representation]
        raise ValueError("No valid graph representation found.")

    def is_vertexes_adjacent(self, vertex_a: Vertex, vertex_b: Vertex) -> bool:
        representation_priority = [GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX, GraphRepresentationType.INCIDENCE]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.is_adjacent_vertex(vertex_a, vertex_b)

    def is_edges_adjacent(self, edge_a: Edge, edge_b: Edge) -> bool:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.is_adjacent_edges(edge_a, edge_b)

    def is_edge_incidencing_in_vertex(self, edge: Edge, vertex: Vertex) -> bool:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.is_edge_incidencing_in_vertex(edge, vertex)
    
    def edge_exists(self, edge: Edge) -> bool:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.edge_exists(edge)
    
    def get_quantity_of_edges(self) -> int:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.get_quantity_of_edges()
    
    def get_quantity_of_vertices(self) -> int:
        return self.quantity_of_vertices
    
    def is_empty(self) -> bool:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.is_empty()
    
    def is_complete_graph(self) -> bool:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.is_complete_graph()
    
    def export_graph(self) -> str:
        representation_priority = [GraphRepresentationType.INCIDENCE, GraphRepresentationType.ADJACENCY_LIST, GraphRepresentationType.ADJACENCY_MATRIX]
        representation = self.__get_first_disponible_representation(representation_priority)
        return representation.export_graph(output_dir=None, edges_info=self.__edges_info, vertices_info=self.__vertexes_info)