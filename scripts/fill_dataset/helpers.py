from time import sleep
import requests

from scripts.fill_dataset.constants import DEFAULT_GITHUB_HEADERS, GITHUB_API_URL


def run_query(query: str, variables: dict) -> dict:
    response = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=DEFAULT_GITHUB_HEADERS)
    response.raise_for_status()
    response = response.json()
    print('Response gotten from GitHub API, sleeping for 0.5 seconds to avoid rate limiting.')
    sleep(0.5)
    return response
