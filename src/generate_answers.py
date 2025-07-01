import os
import json
from collections import defaultdict, Counter
from models.graph.graph_components.edge import EdgeInfoTypes
from models.graph.graph_components.vertex import VertexInfoTypes
from models.social_graph import SocialGraph

DATA_DIR = os.path.join(os.path.dirname(__file__), '../resources')

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def build_social_graph():
    pr_merge = load_json('interactions_pr_merge.json')
    pr_reviews = load_json('interactions_pr_reviews.json')
    issue_comments = load_json('interactions_issue_comments.json')
    pr_comments = load_json('interactions_pr_comments.json')
    mentions = load_json('interactions_mentions.json')
    positive_reactions = load_json('interactions_positive_reactions.json')
    negative_reactions = load_json('interactions_negative_reactions.json')

    edge_weights = defaultdict(int)
    users = set()

    # A abre PR e B faz merge -> peso 3
    for interaction in pr_merge:
        A, B = interaction['A'], interaction['B']
        if A and B:
            edge_weights[(A, B)] += 3
            users.update([A, B])

    # B aprova/solicita mudanças no PR de A -> peso 2
    for interaction in pr_reviews:
        A, B = interaction['A'], interaction['B']
        if A and B:
            edge_weights[(B, A)] += 2
            users.update([A, B])

    # B comenta na Issue/PR de A -> peso 2
    for interaction in issue_comments + pr_comments:
        A, B = interaction['A'], interaction['B']
        if A and B:
            edge_weights[(B, A)] += 2
            users.update([A, B])

    # A menciona B -> peso 1
    for interaction in mentions:
        A, B = interaction['A'], interaction['B']
        if A and B:
            edge_weights[(A, B)] += 1
            users.update([A, B])

    # A reage em um comentário de B -> peso 1
    for interaction in positive_reactions + negative_reactions:
        A, B = interaction['A'], interaction['B']
        if A and B:
            edge_weights[(A, B)] += 1  # A reage ao comentário de B
            users.update([A, B])

    user_list = sorted(users)
    user_to_vertex = {user: i for i, user in enumerate(user_list)}
    vertex_to_user = {i: user for i, user in enumerate(user_list)}

    g = SocialGraph(len(users))

    for user, vertex in user_to_vertex.items():
        g.add_vertex_info(VertexInfoTypes.LABEL, vertex, user)

    for (user_a, user_b), weight in edge_weights.items():
        vertex_a = user_to_vertex[user_a]
        vertex_b = user_to_vertex[user_b]
        g.create_edge(vertex_a, vertex_b)
        g.add_edge_info(EdgeInfoTypes.WEIGHT, (vertex_a, vertex_b), weight)

    return g

def main():
    print("Construindo grafo social...")
    g = build_social_graph()

    print(f"\nGrafo construído com {g.get_quantity_of_vertices()} usuários e {g.get_quantity_of_edges()} arestas.\n")
    
    print("=== 5 USUÁRIOS MAIS INFLUENTES ===")
    influential = g.most_influential_users(5)
    for i, (user, score) in enumerate(influential, 1):
        print(f"{i}. {user}: {score} pontos")
    
    print("\n=== USUÁRIO QUE GERA MAIOR FRAGMENTAÇÃO ===")
    fragmenter, fragmentation_level = g.find_most_fragmenting_user()
    if fragmenter:
        print(f"Usuário mais fragmentador: {fragmenter}")
        print(f"Nível de fragmentação: {fragmentation_level} componentes adicionais")

        original_components = len(g.find_communities_simple())
        print(f"Componentes antes da remoção: {original_components}")
        print(f"Componentes após remoção: {original_components + fragmentation_level}")
    
    print("\n=== GRUPOS NATURAIS (COMUNIDADES) ===")
    communities = g.find_communities_simple()
    for i, community in enumerate(communities, 1):
        print(f"Grupo {i} ({len(community)} membros): {', '.join(community[:5])}")
        if len(community) > 5:
            print(f"  ... e mais {len(community) - 5} membros")
    
    print("\n=== NÍVEL DE CONEXÃO DA COMUNIDADE ===")
    connection = g.connection_level()
    print(f"Nível de conexão: {connection:.2f}%")
    
    print("\n=== ANÁLISE POR USUÁRIO ===")
    example_user = influential[0][0]
    print(f"Analisando usuário: {example_user}")
    
    closest = g.closest_users(example_user, 5)
    print(f"\nMais próximos de {example_user}:")
    for user, score in closest:
        print(f"  - {user}: {score} pontos")
    
    non_direct = g.closest_non_direct_users(example_user, 5)
    print(f"\nMais próximos que não interagem diretamente:")
    for user, distance in non_direct:
        print(f"  - {user}: distância {distance}")

if __name__ == '__main__':
    main()