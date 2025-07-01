import os
import json
import pandas as pd
from scripts.fill_dataset.constants import ISSUES_QUERY, ISSUES_COMMENTS_QUERY, ISSUES_REACTIONS_QUERY, REPO_NAME, REPO_OWNER
from scripts.fill_dataset.helpers import run_query

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../resources')
os.makedirs(DATA_DIR, exist_ok=True)

ISSUES_CSV = os.path.join(DATA_DIR, 'issues_raw.csv')
COMMENTS_CSV = os.path.join(DATA_DIR, 'comments_raw.csv')
REACTIONS_CSV = os.path.join(DATA_DIR, 'reactions_raw.csv')

ISSUES_CURSOR_FILE = os.path.join(DATA_DIR, 'issues_cursor.json')
COMMENTS_CURSORS_FILE = os.path.join(DATA_DIR, 'comments_cursors.json')
REACTIONS_CURSORS_FILE = os.path.join(DATA_DIR, 'reactions_cursors.json')

def save_cursor(filepath, cursor):
    with open(filepath, 'w') as f:
        json.dump({'endCursor': cursor}, f)

def load_cursor(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f).get('endCursor')
    return None

def load_entity_cursors(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_entity_cursors(filepath, cursors):
    with open(filepath, 'w') as f:
        json.dump(cursors, f)

def append_to_csv(filepath, rows, columns):
    df = pd.DataFrame(rows)
    if not os.path.exists(filepath):
        df.to_csv(filepath, index=False, columns=columns)
    else:
        df.to_csv(filepath, mode='a', header=False, index=False, columns=columns)

def fetch_all_issues():
    issues_cursor = load_cursor(ISSUES_CURSOR_FILE)
    page = 1
    while True:
        print(f"[Issues] Fetching page {page} (cursor={issues_cursor})...")
        variables = {
            'owner': REPO_OWNER,
            'name': REPO_NAME
        }
        if issues_cursor:
            variables['cursor'] = issues_cursor
        response = run_query(ISSUES_QUERY, variables)
        repo_issues = response['data']['repository']['issues']
        print(f"[Issues] Fetched {len(repo_issues['nodes'])} issues.")
        for issue in repo_issues['nodes']:
            print(f"[Issues] Processing issue #{issue['number']} ({issue['id']})")
            append_to_csv(
                ISSUES_CSV,
                [{
                    'id': issue['id'],
                    'number': issue['number'],
                    'bodyText': issue['bodyText'],
                    'createdAt': issue['createdAt'],
                    'closedAt': issue['closedAt'],
                    'author': issue['author']['login'] if issue['author'] else None,
                }],
                ['id', 'number', 'bodyText', 'createdAt', 'closedAt', 'author']
            )
            fetch_all_comments_for_issue(issue['number'])
        issues_cursor = repo_issues['pageInfo']['endCursor']
        save_cursor(ISSUES_CURSOR_FILE, issues_cursor)
        if not repo_issues['pageInfo']['hasNextPage']:
            print("[Issues] No more pages.")
            break
        page += 1

def fetch_all_comments_for_issue(issue_number):
    comments_cursors = load_entity_cursors(COMMENTS_CURSORS_FILE)
    comments_cursor = comments_cursors.get(str(issue_number))
    page = 1
    while True:
        print(f"  [Comments] Fetching page {page} for issue #{issue_number} (cursor={comments_cursor})...")
        variables = {
            'owner': REPO_OWNER,
            'name': REPO_NAME,
            'number': issue_number,
        }
        if comments_cursor:
            variables['cursor'] = comments_cursor
        response = run_query(ISSUES_COMMENTS_QUERY, variables)
        comments = response['data']['repository']['issue']['comments']
        print(f"  [Comments] Fetched {len(comments['nodes'])} comments.")
        for comment in comments['nodes']:
            print(f"  [Comments] Processing comment {comment['id']}")
            append_to_csv(
                COMMENTS_CSV,
                [{
                    'issue_number': issue_number,
                    'id': comment['id'],
                    'author': comment['author']['login'] if comment['author'] else None,
                    'bodyText': comment['bodyText'],
                    'createdAt': comment['createdAt']
                }],
                ['issue_number', 'id', 'author', 'bodyText', 'createdAt']
            )
            fetch_all_reactions_for_comment(comment['id'])
        comments_cursor = comments['pageInfo']['endCursor']
        comments_cursors[str(issue_number)] = comments_cursor
        save_entity_cursors(COMMENTS_CURSORS_FILE, comments_cursors)
        if not comments['pageInfo']['hasNextPage']:
            print(f"  [Comments] No more pages for issue #{issue_number}.")
            comments_cursors.pop(str(issue_number), None)
            save_entity_cursors(COMMENTS_CURSORS_FILE, comments_cursors)
            break
        page += 1

def fetch_all_reactions_for_comment(comment_id):
    reactions_cursors = load_entity_cursors(REACTIONS_CURSORS_FILE)
    reactions_cursor = reactions_cursors.get(str(comment_id))
    page = 1
    while True:
        print(f"    [Reactions] Fetching page {page} for comment {comment_id} (cursor={reactions_cursor})...")
        variables = {
            'id': comment_id
        }
        if reactions_cursor:
            variables['cursor'] = reactions_cursor
        response = run_query(ISSUES_REACTIONS_QUERY, variables)
        reactions = response['data']['node']['reactions']
        print(f"    [Reactions] Fetched {len(reactions['nodes'])} reactions.")
        for reaction in reactions['nodes']:
            print(f"    [Reactions] Processing reaction by {reaction['user']['login'] if reaction['user'] else 'unknown'}")
            append_to_csv(
                REACTIONS_CSV,
                [{
                    'comment_id': comment_id,
                    'user': reaction['user']['login'] if reaction['user'] else None,
                    'content': reaction['content']
                }],
                ['comment_id', 'user', 'content']
            )
        reactions_cursor = reactions['pageInfo']['endCursor']
        reactions_cursors[str(comment_id)] = reactions_cursor
        save_entity_cursors(REACTIONS_CURSORS_FILE, reactions_cursors)
        if not reactions['pageInfo']['hasNextPage']:
            print(f"    [Reactions] No more pages for comment {comment_id}.")
            reactions_cursors.pop(str(comment_id), None)
            save_entity_cursors(REACTIONS_CURSORS_FILE, reactions_cursors)
            break
        page += 1