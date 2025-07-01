GITHUB_TOKEN = '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'
REPO_OWNER = 'vuejs'
REPO_NAME = 'core'
DEFAULT_GITHUB_HEADERS = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
GITHUB_API_URL = 'https://api.github.com/graphql'


ISSUES_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 50, after: $cursor, orderBy: {field: CREATED_AT, direction: ASC}) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        number
        bodyText
        createdAt
        closedAt
        author { login }
      }
    }
  }
}
"""
ISSUES_COMMENTS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    issue(number: $number) {
      comments(first: 50, after: $cursor) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          id
          author { login }
          bodyText
          createdAt
        }
      }
    }
  }
}
"""
ISSUES_REACTIONS_QUERY = """
query($id: ID!, $cursor: String) {
  node(id: $id) {
    ... on IssueComment {
      reactions(first: 50, after: $cursor) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          user { login }
          content
        }
      }
    }
  }
}
"""

PRS_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 30, after: $cursor, orderBy: {field: CREATED_AT, direction: ASC}) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        number
        bodyText
        createdAt
        closedAt
        mergedAt
        author { login }
        mergedBy { login }
      }
    }
  }
}
"""

PRS_COMMENTS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      comments(first: 50, after: $cursor) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          id
          author { login }
          bodyText
          createdAt
        }
      }
    }
  }
}
"""

PRS_REVIEWS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: 50, after: $cursor) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          id
          author { login }
          state
          body
          createdAt
        }
      }
    }
  }
}
"""