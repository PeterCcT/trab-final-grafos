import pandas as pd
import json
import os
import re
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), '../resources')

def load_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_json(data: List[Dict[str, Any]], filename: str) -> None:
    with open(os.path.join(DATA_DIR, filename), 'w') as f:
        json.dump(data, f, indent=2)

def is_valid_interaction(user_a: str, user_b: str) -> bool:
    return (pd.notna(user_a) and 
            pd.notna(user_b) and 
            user_a != user_b)

def extract_pr_merge_interactions(prs: pd.DataFrame) -> List[Dict[str, Any]]:
    interactions = []
    
    for _, row in prs.iterrows():
        author = row.get('author')
        merged_by = row.get('mergedBy')
        
        if is_valid_interaction(author, merged_by):
            interactions.append({
                'pr_number': row['number'],
                'A': author,
                'B': merged_by,
                'action': 'merged',
                'at': row['mergedAt']
            })
    
    return interactions

def extract_pr_review_interactions(pr_reviews: pd.DataFrame, prs: pd.DataFrame) -> List[Dict[str, Any]]:
    if pr_reviews.empty:
        return []
    
    interactions = []
    pr_authors = prs.set_index('number')['author'].to_dict()
    valid_states = ['APPROVED', 'CHANGES_REQUESTED']
    
    for _, row in pr_reviews.iterrows():
        pr_number = row['pr_number']
        pr_author = pr_authors.get(pr_number)
        reviewer = row.get('author')
        
        if (is_valid_interaction(pr_author, reviewer) and 
            row['state'] in valid_states):
            interactions.append({
                'pr_number': pr_number,
                'A': pr_author,
                'B': reviewer,
                'state': row['state'],
                'at': row['createdAt']
            })
    
    return interactions

def extract_comment_interactions(comments: pd.DataFrame, authors_map: Dict[int, str]) -> List[Dict[str, Any]]:
    if comments.empty:
        return []
    
    interactions = []
    grouped = comments.groupby(['issue_number' if 'issue_number' in comments.columns else 'pr_number', 'author']).size().reset_index(name='count')
    
    for _, row in grouped.iterrows():
        content_number = row.iloc[0]
        commenter = row['author']
        content_author = authors_map.get(content_number)
        
        if is_valid_interaction(content_author, commenter):
            interaction_key = 'issue_number' if 'issue_number' in comments.columns else 'pr_number'
            interactions.append({
                interaction_key: content_number,
                'A': content_author,
                'B': commenter,
                'count': int(row['count'])
            })
    
    return interactions

def extract_reaction_interactions(reactions: pd.DataFrame, comment_authors: Dict[str, str]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    positive_types = {'THUMBS_UP', 'HEART', 'HOORAY', 'ROCKET'}
    negative_types = {'THUMBS_DOWN', 'CONFUSED'}
    
    positive_interactions = []
    negative_interactions = []
    
    for _, row in reactions.iterrows():
        reactor = row['user']
        comment_id = row['comment_id']
        comment_author = comment_authors.get(comment_id)
        reaction_type = row['content']
        
        if is_valid_interaction(reactor, comment_author):
            interaction = {
                'A': reactor,
                'B': comment_author,
                'comment_id': comment_id,
                'reaction': reaction_type
            }
            
            if reaction_type in positive_types:
                positive_interactions.append(interaction)
            elif reaction_type in negative_types:
                negative_interactions.append(interaction)
    
    return positive_interactions, negative_interactions

def extract_mention_interactions(comments: pd.DataFrame) -> List[Dict[str, Any]]:
    interactions = []
    
    for _, row in comments.iterrows():
        author = row['author']
        body = row.get('bodyText', '')
        
        if pd.isna(author) or not isinstance(body, str):
            continue

        mentions = set(re.findall(r'@([a-zA-Z0-9-]+)', body))
        
        for mentioned_user in mentions:
            if author != mentioned_user:
                interactions.append({
                    'A': author,
                    'B': mentioned_user,
                    'comment_id': row['id']
                })
    
    return interactions

def main():
    print("Carregando dados...")
    issues = load_csv('issues_raw.csv')
    prs = load_csv('prs_raw.csv')
    issue_comments = load_csv('comments_raw.csv')
    pr_comments = load_csv('pr_comments_raw.csv')
    pr_reviews = load_csv('pr_reviews_raw.csv')
    reactions = load_csv('reactions_raw.csv')
    
    print("Processando interações...")
    
    print("  - Extraindo interações de merge...")
    pr_merge_interactions = extract_pr_merge_interactions(prs)
    save_json(pr_merge_interactions, 'interactions_pr_merge.json')
    
    print("  - Extraindo interações de review...")
    pr_review_interactions = extract_pr_review_interactions(pr_reviews, prs)
    save_json(pr_review_interactions, 'interactions_pr_reviews.json')
    
    print("  - Extraindo interações de comentários...")
    issue_authors = issues.set_index('number')['author'].to_dict()
    pr_authors = prs.set_index('number')['author'].to_dict()
    issue_comment_interactions = extract_comment_interactions(issue_comments, issue_authors)
    pr_comment_interactions = extract_comment_interactions(pr_comments, pr_authors)
    
    save_json(issue_comment_interactions, 'interactions_issue_comments.json')
    save_json(pr_comment_interactions, 'interactions_pr_comments.json')
    
    print("  - Extraindo interações de reações...")
    all_comments = pd.concat([
        issue_comments.rename(columns={'issue_number': 'parent_number'}),
        pr_comments.rename(columns={'pr_number': 'parent_number'})
    ], ignore_index=True)
    
    comment_authors = all_comments.set_index('id')['author'].to_dict()
    positive_reactions, negative_reactions = extract_reaction_interactions(reactions, comment_authors)
    
    save_json(positive_reactions, 'interactions_positive_reactions.json')
    save_json(negative_reactions, 'interactions_negative_reactions.json')
    
    print("  - Extraindo interações de menções...")
    mention_interactions = extract_mention_interactions(all_comments)
    save_json(mention_interactions, 'interactions_mentions.json')
    
    print("Processamento concluído!")
    print(f"  - {len(pr_merge_interactions)} interações de merge")
    print(f"  - {len(pr_review_interactions)} interações de review")
    print(f"  - {len(issue_comment_interactions)} interações de comentários em issues")
    print(f"  - {len(pr_comment_interactions)} interações de comentários em PRs")
    print(f"  - {len(positive_reactions)} reações positivas")
    print(f"  - {len(negative_reactions)} reações negativas")
    print(f"  - {len(mention_interactions)} menções")

if __name__ == '__main__':
    main()