from models.graph.graph import Graph
from models.graph.graph_components.edge import Edge, EdgeInfoTypes
from models.graph.graph_components.vertex import Vertex, VertexInfoTypes


class SocialGraph(Graph):
    def __init__(self, quantity_of_vertices: int):
        super().__init__(quantity_of_vertices)
    
    def get_vertex_label(self, vertex: Vertex) -> str:
        return self.get_vertex_info(VertexInfoTypes.LABEL, vertex)

    def get_edge_weight(self, edge: Edge) -> int:
        edge_info = self.get_edge_info(EdgeInfoTypes.WEIGHT, edge)
        if edge_info is not None:
            return edge_info
        inverted_edge = (edge[1], edge[0])
        edge_info = self.get_edge_info(EdgeInfoTypes.WEIGHT, inverted_edge)
        if edge_info is not None:
            return edge_info
            
        return 0

    def get_vertices(self) -> list[Vertex]:
        return list(range(self.quantity_of_vertices))
    
    def get_edges(self) -> list[Edge]:
        edges_set = set()
        for edge in self._Graph__edges_info.keys():
            normalized_edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))
            edges_set.add(normalized_edge)
        return list(edges_set)
    
    def get_edges_with_weights(self) -> list[tuple[Edge, int]]:
        edges_weights = []
        for edge in self.get_edges():
            weight = self.get_edge_weight(edge)
            edges_weights.append((edge, weight))
        return edges_weights
    
    def get_vertex_degree(self, vertex: Vertex) -> int:
        degree = 0
        processed_edges = set()
        
        for edge in self._Graph__edges_info.keys():
            if vertex in edge:
                normalized_edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))
                if normalized_edge not in processed_edges:
                    processed_edges.add(normalized_edge)
                    degree += 1
        return degree
    
    def get_vertex_weighted_degree(self, vertex: Vertex) -> int:
        weighted_degree = 0
        processed_edges = set()
        
        for edge in self._Graph__edges_info.keys():
            if vertex in edge:
                normalized_edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))
                if normalized_edge not in processed_edges:
                    processed_edges.add(normalized_edge)
                    weight = self.get_edge_weight(edge)
                    weighted_degree += weight
        return weighted_degree
    
    def get_neighbors(self, vertex: Vertex) -> list[Vertex]:
        neighbors = set()
        for edge in self._Graph__edges_info.keys():
            if edge[0] == vertex:
                neighbors.add(edge[1])
            elif edge[1] == vertex:
                neighbors.add(edge[0])
        return list(neighbors)
    
    def most_influential_users(self, top_n: int = 5) -> list[tuple[str, int]]:
        influence_scores = {}
        
        for vertex in self.get_vertices():
            influence_scores[vertex] = self.get_vertex_weighted_degree(vertex)
        
        sorted_vertices = sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for vertex, score in sorted_vertices[:top_n]:
            user_label = self.get_vertex_label(vertex)
            result.append((user_label, score))
        
        return result
    
    def find_communities_simple(self) -> list[list[str]]:
        # Basicamente uma busca em profundidade até encontrar todos os vértices conectados
        # Se tiver um vértice não visitado, inicia um novo compontente (comunidade)
        visited = set()
        communities = []
        
        def dfs(vertex, community):
            visited.add(vertex)
            community.append(vertex)
            for neighbor in self.get_neighbors(vertex):
                if neighbor not in visited:
                    dfs(neighbor, community)
        
        for vertex in self.get_vertices():
            if vertex not in visited:
                community = []
                dfs(vertex, community)
                if len(community) > 1:
                    user_community = [self.get_vertex_label(v) for v in community]
                    communities.append(user_community)
        
        return communities
    
    def connection_level(self) -> float:
        # Pega a qtd de usuarios total ai calcula quantos pares são possíveis
        # Ai para vértice ele faz uma busca em largura pra ver quem ele consegue alcançar
        # Conta quantos pares de usuários estão conectados (ai pode ser direto ou indireto)
        # Divide pelo total de pares possíveis
        vertices = self.get_vertices()
        n = len(vertices)
        
        if n <= 1:
            return 100.0

        total_possible_pairs = n * (n - 1) // 2
        connected_pairs = set()
        
        for start_vertex in vertices:
            visited = set([start_vertex])
            queue = [start_vertex]
            
            while queue:
                current = queue.pop(0)
                for neighbor in self.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        pair = (min(start_vertex, neighbor), max(start_vertex, neighbor))
                        connected_pairs.add(pair)
        
        connection_percentage = (len(connected_pairs) * 100) / total_possible_pairs
        return connection_percentage
    
    def closest_users(self, user_label: str, top_n: int = 5) -> list[tuple[str, int]]:
        target_vertex = None
        for vertex in self.get_vertices():
            if self.get_vertex_label(vertex) == user_label:
                target_vertex = vertex
                break
        
        if target_vertex is None:
            return []
        
        scores = {}
        processed_edges = set()
        
        for edge in self._Graph__edges_info.keys():
            if target_vertex in edge:
                normalized_edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))
                if normalized_edge not in processed_edges:
                    processed_edges.add(normalized_edge)
                    weight = self.get_edge_weight(edge)
                    neighbor = edge[1] if edge[0] == target_vertex else edge[0]
                    scores[neighbor] = scores.get(neighbor, 0) + weight
        
        sorted_neighbors = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for vertex, score in sorted_neighbors[:top_n]:
            neighbor_label = self.get_vertex_label(vertex)
            result.append((neighbor_label, score))
        
        return result
    
    def closest_non_direct_users(self, user_label: str, top_n: int = 5) -> list[tuple[str, int]]:
        target_vertex = None
        for vertex in self.get_vertices():
            if self.get_vertex_label(vertex) == user_label:
                target_vertex = vertex
                break
        
        if target_vertex is None:
            return []
        
        direct_neighbors = set(self.get_neighbors(target_vertex))
        direct_neighbors.add(target_vertex)
        
        distances = {target_vertex: 0}
        queue = [target_vertex]
        visited = set([target_vertex])
        
        while queue:
            current = queue.pop(0)
            current_distance = distances[current]
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = current_distance + 1
                    queue.append(neighbor)

        non_direct_users = []
        for vertex, distance in distances.items():
            if vertex not in direct_neighbors and distance > 0:
                user_label_vertex = self.get_vertex_label(vertex)
                non_direct_users.append((user_label_vertex, distance))
        
        non_direct_users.sort(key=lambda x: x[1])
        return non_direct_users[:top_n]

    def find_most_fragmenting_user(self) -> tuple[str, int]:
        # Pega os componentes conectados originais
        # Ai remove vértice por vértice e vê qual acaba gerando mais componentes
        # O usuário que mais fragmenta basicamente seria o usuário que mais gera novos componentes
        original_components = len(self.find_communities_simple())
        max_fragmentation = 0
        most_fragmenting_user = None
        
        for vertex in self.get_vertices():
            edges_to_remove = []
            edges_info_backup = {}
            
            for edge in list(self._Graph__edges_info.keys()):
                if vertex in edge:
                    edges_to_remove.append(edge)
                    edges_info_backup[edge] = self._Graph__edges_info[edge].copy()
            
            for edge in edges_to_remove:
                del self._Graph__edges_info[edge]
                self.delete_edge(edge[0], edge[1])
            
            new_components = len(self.find_communities_simple())
            fragmentation = new_components - original_components
            
            if fragmentation > max_fragmentation:
                max_fragmentation = fragmentation
                most_fragmenting_user = self.get_vertex_label(vertex)
            
            for edge in edges_to_remove:
                self.create_edge(edge[0], edge[1])
                self._Graph__edges_info[edge] = edges_info_backup[edge]
        
        return most_fragmenting_user, max_fragmentation