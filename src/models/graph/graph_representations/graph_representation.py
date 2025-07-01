import os
import networkx as nx
from abc import ABC, abstractmethod
from typing import Any

from models.graph.graph_components.edge import Edge, EdgeInfoTypes
from models.graph.graph_components.vertex import Vertex, VertexInfoTypes
from models.graph.graph_representations.graph_representations_types import GraphRepresentationType

class GraphRepresentation(ABC):
    def __init__(self, representation_type: GraphRepresentationType, quantity_of_vertices: int):
        self.representation_type = representation_type
        self.quantity_of_vertices = quantity_of_vertices
    
    @abstractmethod
    def create_edge(self, vertex_a: Vertex, vertex_b: Vertex) -> None:
        pass

    @abstractmethod
    def delete_edge(self, vertex_a: Vertex, vertex_b: Vertex) -> None:
        pass

    @abstractmethod
    def is_adjacent_vertex(self, vertex_a: Vertex, vertex_b: Vertex) -> bool:
        pass

    @abstractmethod
    def is_adjacent_edges(self, edge_a: Edge, edge_b: Edge) -> bool:
        pass

    @abstractmethod
    def is_edge_incidencing_in_vertex(self, edge: Edge, vertex: Vertex) -> bool:
        pass
    
    @abstractmethod
    def edge_exists(self, edge: Edge) -> bool:
        pass
    
    @abstractmethod
    def get_quantity_of_edges(self) -> int:
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        pass
    
    @abstractmethod
    def is_complete_graph(self) -> bool:
        pass
    
    @abstractmethod
    def get_edges(self) -> set[Edge]:
        raise NotImplementedError

    def __get_gephi_graph(self, vertices_info: dict[Vertex, dict[VertexInfoTypes, Any]] | None, edges_info: dict[Edge, dict[EdgeInfoTypes, Any]] | None) -> nx.Graph:
        gephi_graph = nx.Graph()
        for vertex in range(self.quantity_of_vertices):
            gephi_graph.add_node(vertex, label=f"{vertex}")
            if vertices_info and vertex in vertices_info:
                nx.set_node_attributes(gephi_graph, {vertex: vertices_info[vertex]})
        self.__fill_edges_in_gephi_graph(gephi_graph, edges_info)
        return gephi_graph

    def __fill_edges_in_gephi_graph(self, gephi_graph: nx.Graph, edges_info: dict[Edge, dict[EdgeInfoTypes, Any]] | None) -> None:
        edges = self.get_edges()
        for edge in edges:
            edge_info = edges_info.get(edge, {}) if edges_info else {}
            gephi_graph.add_edge(*edge, **edge_info)

    def export_graph(self, output_dir: str | None = None, 
                    edges_info: dict[Edge, dict[EdgeInfoTypes, Any]] | None = None, 
                    vertices_info: dict[Vertex, dict[VertexInfoTypes, Any]] | None = None) -> str:
        gephi_graph = self.__get_gephi_graph(vertices_info, edges_info)

        if output_dir is None:
            output_dir = os.getcwd()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        gexf_file = os.path.join(output_dir, f"graph_2.gexf")
        nx.write_gexf(gephi_graph, gexf_file)
        return gexf_file