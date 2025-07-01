import os
import json
import pandas as pd
from scripts.fill_dataset.constants import PRS_QUERY, PRS_COMMENTS_QUERY, PRS_REVIEWS_QUERY, REPO_NAME, REPO_OWNER
from scripts.fill_dataset.helpers import run_query

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../resources')
os.makedirs(DATA_DIR, exist_ok=True)

PRS_CSV = os.path.join(DATA_DIR, 'prs_raw.csv')
PR_COMMENTS_CSV = os.path.join(DATA_DIR, 'pr_comments_raw.csv')
PR_REVIEWS_CSV = os.path.join(DATA_DIR, 'pr_reviews_raw.csv')

PRS_CURSOR_FILE = os.path.join(DATA_DIR, 'prs_cursor.json')
PR_COMMENTS_CURSORS_FILE = os.path.join(DATA_DIR, 'pr_comments_cursors.json')
PR_REVIEWS_CURSORS_FILE = os.path.join(DATA_DIR, 'pr_reviews_cursors.json')

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

def fetch_all_prs():
    prs_cursor = load_cursor(PRS_CURSOR_FILE)
    page = 1
    while True:
        print(f"[PRs] Fetching page {page} (cursor={prs_cursor})...")
        variables = {
            'owner': REPO_OWNER,
            'name': REPO_NAME
        }
        if prs_cursor:
            variables['cursor'] = prs_cursor
        response = run_query(PRS_QUERY, variables)
        repo_prs = response['data']['repository']['pullRequests']
        print(f"[PRs] Fetched {len(repo_prs['nodes'])} PRs.")
        for pr in repo_prs['nodes']:
            print(f"[PRs] Processing PR #{pr['number']} ({pr['id']})")
            append_to_csv(
                PRS_CSV,
                [{
                    'id': pr['id'],
                    'number': pr['number'],
                    'bodyText': pr['bodyText'],
                    'createdAt': pr['createdAt'],
                    'closedAt': pr['closedAt'],
                    'mergedAt': pr['mergedAt'],
                    'author': pr['author']['login'] if pr['author'] else None,
                    'mergedBy': pr['mergedBy']['login'] if pr.get('mergedBy') and pr['mergedBy'] else None,
                    'closedBy': pr['closedBy']['login'] if pr.get('closedBy') and pr['closedBy'] else None,
                }],
                ['id', 'number', 'bodyText', 'createdAt', 'closedAt', 'mergedAt', 'author', 'mergedBy', 'closedBy']
            )
            fetch_all_comments_for_pr(pr['number'])
            fetch_all_reviews_for_pr(pr['number'])
        prs_cursor = repo_prs['pageInfo']['endCursor']
        save_cursor(PRS_CURSOR_FILE, prs_cursor)
        if not repo_prs['pageInfo']['hasNextPage']:
            print("[PRs] No more pages.")
            break
        page += 1

def fetch_all_comments_for_pr(pr_number):
    comments_cursors = load_entity_cursors(PR_COMMENTS_CURSORS_FILE)
    comments_cursor = comments_cursors.get(str(pr_number))
    page = 1
    while True:
        print(f"  [PR Comments] Fetching page {page} for PR #{pr_number} (cursor={comments_cursor})...")
        variables = {
            'owner': REPO_OWNER,
            'name': REPO_NAME,
            'number': pr_number,
        }
        if comments_cursor:
            variables['cursor'] = comments_cursor
        response = run_query(PRS_COMMENTS_QUERY, variables)
        comments = response['data']['repository']['pullRequest']['comments']
        print(f"  [PR Comments] Fetched {len(comments['nodes'])} comments.")
        for comment in comments['nodes']:
            print(f"  [PR Comments] Processing comment {comment['id']}")
            append_to_csv(
                PR_COMMENTS_CSV,
                [{
                    'pr_number': pr_number,
                    'id': comment['id'],
                    'author': comment['author']['login'] if comment['author'] else None,
                    'bodyText': comment['bodyText'],
                    'createdAt': comment['createdAt']
                }],
                ['pr_number', 'id', 'author', 'bodyText', 'createdAt']
            )
        comments_cursor = comments['pageInfo']['endCursor']
        comments_cursors[str(pr_number)] = comments_cursor
        save_entity_cursors(PR_COMMENTS_CURSORS_FILE, comments_cursors)
        if not comments['pageInfo']['hasNextPage']:
            print(f"  [PR Comments] No more pages for PR #{pr_number}.")
            comments_cursors.pop(str(pr_number), None)
            save_entity_cursors(PR_COMMENTS_CURSORS_FILE, comments_cursors)
            break
        page += 1

def fetch_all_reviews_for_pr(pr_number):
    reviews_cursors = load_entity_cursors(PR_REVIEWS_CURSORS_FILE)
    reviews_cursor = reviews_cursors.get(str(pr_number))
    page = 1
    while True:
        print(f"  [PR Reviews] Fetching page {page} for PR #{pr_number} (cursor={reviews_cursor})...")
        variables = {
            'owner': REPO_OWNER,
            'name': REPO_NAME,
            'number': pr_number,
        }
        if reviews_cursor:
            variables['cursor'] = reviews_cursor
        response = run_query(PRS_REVIEWS_QUERY, variables)
        reviews = response['data']['repository']['pullRequest']['reviews']
        print(f"  [PR Reviews] Fetched {len(reviews['nodes'])} reviews.")
        for review in reviews['nodes']:
            print(f"  [PR Reviews] Processing review {review['id']}")
            append_to_csv(
                PR_REVIEWS_CSV,
                [{
                    'pr_number': pr_number,
                    'id': review['id'],
                    'author': review['author']['login'] if review['author'] else None,
                    'state': review['state'],
                    'body': review['body'],
                    'createdAt': review['createdAt']
                }],
                ['pr_number', 'id', 'author', 'state', 'body', 'createdAt']
            )
        reviews_cursor = reviews['pageInfo']['endCursor']
        reviews_cursors[str(pr_number)] = reviews_cursor
        save_entity_cursors(PR_REVIEWS_CURSORS_FILE, reviews_cursors)
        if not reviews['pageInfo']['hasNextPage']:
            print(f"  [PR Reviews] No more pages for PR #{pr_number}.")
            reviews_cursors.pop(str(pr_number), None)
            save_entity_cursors(PR_REVIEWS_CURSORS_FILE, reviews_cursors)
            break
        page += 1