import requests
import time
import os

URL = "https://api.github.com/graphql"


GRAPHQL_QUERY = """
query ($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    # 1. Dados básicos do repositório
    name
    description
    url
    stargazerCount
    forkCount
    watchers {
      totalCount
    }
    openIssues: issues(states: [OPEN]) {
      totalCount
    }
    createdAt
    updatedAt
    primaryLanguage {
      name
    }
    licenseInfo {
      name
    }
    repositoryTopics(first: 20) {
      nodes {
        topic {
          name
        }
      }
    }

    # 2. Linguagens utilizadas
    languages(first: 100, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        size
        node {
          name
        }
      }
    }

    # 3. Issues abertas (60 mais recentes)
    issues(first: 60, states: [OPEN], orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        title
        number
        state
        createdAt
        author {
          login
        }
        labels(first: 10) {
          nodes {
            name
          }
        }
      }
    }

    # 4. Pull Requests abertos (10 mais recentes para coletar reviews)
    pullRequests(first: 10, states: [OPEN], orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        title
        number
        state
        createdAt
        author {
          login
        }
        mergeable 

        # 4a. Reviews associados (até 10 por PR)
        reviews(first: 10, states: [APPROVED, CHANGES_REQUESTED]) {
          nodes {
            state
            author {
              login
            }
          }
        }
      }
    }

    # 5. Commits recentes (60 últimos)
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 60) {
            nodes {
              committedDate
              author {
                name
                email
                user {
                  login
                }
              }
            }
          }
        }
      }
    }

    # 6. Contribuidores (20 principais)
    mentionableUsers(first: 20) {
      nodes {
        login
        name
      }
    }
  } # <--- Fim do objeto 'repository'
  
  # Inclui dados de rate limit na resposta
  rateLimit {
    cost
    remaining
    resetAt
  }
}
"""


def fetch_graphql_data(owner: str, repo: str, token: str):
    """
    Coleta todos os dados definidos no experimento usando a API GraphQL v4.
    Isso usa uma única chamada de rede.
    Também captura informações de rate limit para análise.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }

    variables = {"owner": owner, "repo": repo}

    # Capturar rate limit ANTES da requisição
    rate_limit_before = None
    try:
        pre_check = requests.post(
            URL,
            json={"query": "{ rateLimit { remaining limit resetAt } }"},
            headers=headers,
        )
        if pre_check.status_code == 200:
            pre_data = pre_check.json()
            if "data" in pre_data and "rateLimit" in pre_data["data"]:
                rate_limit_before = pre_data["data"]["rateLimit"]["remaining"]
    except:
        pass  # Se falhar, continua sem o valor

    try:
        start_time = time.perf_counter()
        response = requests.post(
            URL, json={"query": GRAPHQL_QUERY, "variables": variables}, headers=headers
        )
        end_time = time.perf_counter()

        total_time_ms = (end_time - start_time) * 1000
        total_size_bytes = len(response.content)

        response.raise_for_status()

        json_data = response.json()

        if "errors" in json_data:
            raise requests.exceptions.RequestException(json_data["errors"])

        # Capturar rate limit DEPOIS da requisição
        rate_limit_after = None
        rate_limit_cost = None
        rate_limit_reset = None

        if "data" in json_data and "rateLimit" in json_data["data"]:
            rate_limit_info = json_data["data"]["rateLimit"]
            rate_limit_after = rate_limit_info.get("remaining")
            rate_limit_cost = rate_limit_info.get("cost")
            rate_limit_reset = rate_limit_info.get("resetAt")

            if rate_limit_after and rate_limit_after < 200:
                print(
                    f"GraphQL rate limit baixo ({rate_limit_after}). Pausando por 60s..."
                )
                time.sleep(60)

        # Calcular consumo
        rate_limit_consumed = None
        if rate_limit_before is not None and rate_limit_after is not None:
            rate_limit_consumed = rate_limit_before - rate_limit_after

        return {
            "repo": f"{owner}/{repo}",
            "api_type": "GraphQL",
            "response_time_ms": total_time_ms,
            "response_size_bytes": total_size_bytes,
            "num_requests": 1,
            "rate_limit_before": rate_limit_before,
            "rate_limit_after": rate_limit_after,
            "rate_limit_consumed": rate_limit_consumed,
            "rate_limit_cost": rate_limit_cost,
            "rate_limit_reset_at": rate_limit_reset,
            "status": "success",
            "error_message": None,
        }

    except requests.exceptions.RequestException as e:
        total_time_ms = (
            (time.perf_counter() - start_time) * 1000 if "start_time" in locals() else 0
        )
        return {
            "repo": f"{owner}/{repo}",
            "api_type": "GraphQL",
            "response_time_ms": total_time_ms,
            "response_size_bytes": (
                len(response.content) if "response" in locals() else 0
            ),
            "num_requests": 1,
            "rate_limit_before": rate_limit_before,
            "rate_limit_after": None,
            "rate_limit_consumed": None,
            "rate_limit_cost": None,
            "rate_limit_reset_at": None,
            "status": "error",
            "error_message": str(e),
        }
