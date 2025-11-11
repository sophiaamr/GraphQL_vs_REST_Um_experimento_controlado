import requests
import time
import os

BASE_URL = "https://api.github.com"


def fetch_rest_data(owner: str, repo: str, token: str):
    """
    Coleta todos os dados definidos no experimento usando a API REST v3.
    Isso exigirá múltiplas chamadas de rede.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Cache-Control": "no-cache",  # Mitigação de cache
    }

    total_time_ms = 0
    total_size_bytes = 0
    num_requests = 0

    endpoints = [
        f"/repos/{owner}/{repo}",
        f"/repos/{owner}/{repo}/languages",
        f"/repos/{owner}/{repo}/issues?state=open&per_page=60&page=1",
        f"/repos/{owner}/{repo}/pulls?state=open&per_page=60&page=1",
        f"/repos/{owner}/{repo}/commits?per_page=60&page=1",  # 5. Commits
    ]

    collected_data = {}

    try:
        for endpoint in endpoints:
            url = f"{BASE_URL}{endpoint}"
            start_time = time.perf_counter()
            response = requests.get(url, headers=headers)
            end_time = time.perf_counter()

            total_time_ms += (end_time - start_time) * 1000
            total_size_bytes += len(response.content)
            num_requests += 1

            response.raise_for_status()

            if "rate_limit" in response.headers.get("X-RateLimit-Remaining", "5000"):
                remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
                if remaining < 200:
                    print("Rate limit baixo. Pausando por 60s...")
                    time.sleep(60)

            if endpoint.startswith("/repos/{owner}/{repo}/pulls"):
                collected_data["pulls"] = response.json()

        if "pulls" in collected_data:
            for pr in collected_data["pulls"]:
                pr_number = pr["number"]
                reviews_url = (
                    f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
                )

                start_time = time.perf_counter()
                response = requests.get(reviews_url, headers=headers)
                end_time = time.perf_counter()

                total_time_ms += (end_time - start_time) * 1000
                total_size_bytes += len(response.content)
                num_requests += 1
                response.raise_for_status()

        return {
            "repo": f"{owner}/{repo}",
            "api_type": "REST",
            "response_time_ms": total_time_ms,
            "response_size_bytes": total_size_bytes,
            "num_requests": num_requests,
            "status": "success",
            "error_message": None,
        }

    except requests.exceptions.RequestException as e:
        return {
            "repo": f"{owner}/{repo}",
            "api_type": "REST",
            "response_time_ms": total_time_ms,
            "response_size_bytes": total_size_bytes,
            "num_requests": num_requests,
            "status": "error",
            "error_message": str(e),
        }
