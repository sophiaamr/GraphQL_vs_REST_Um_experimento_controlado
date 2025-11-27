import requests
import time
import os

BASE_URL = "https://api.github.com"


def fetch_rest_data(owner: str, repo: str, token: str):
    """
    Coleta todos os dados definidos no experimento usando a API REST v3.
    Isso exigirá múltiplas chamadas de rede.
    Também captura informações de rate limit para análise.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Cache-Control": "no-cache",  # Mitigação de cache
    }

    total_time_ms = 0
    total_size_bytes = 0
    num_requests = 0

    # Capturar rate limit ANTES da primeira requisição
    rate_limit_before = None
    rate_limit_after = None
    rate_limit_reset = None

    endpoints = [
        f"/repos/{owner}/{repo}",
        f"/repos/{owner}/{repo}/languages",
        f"/repos/{owner}/{repo}/issues?state=open&per_page=60&page=1",
        f"/repos/{owner}/{repo}/pulls?state=open&per_page=60&page=1",
        f"/repos/{owner}/{repo}/commits?per_page=60&page=1",  # 5. Commits
        f"/repos/{owner}/{repo}/contributors?per_page=20&page=1",  # 6. Contribuidores
    ]

    collected_data = {}

    try:
        for idx, endpoint in enumerate(endpoints):
            url = f"{BASE_URL}{endpoint}"
            start_time = time.perf_counter()
            response = requests.get(url, headers=headers)
            end_time = time.perf_counter()

            total_time_ms += (end_time - start_time) * 1000
            total_size_bytes += len(response.content)
            num_requests += 1

            response.raise_for_status()

            # Capturar rate limit da PRIMEIRA requisição
            if idx == 0:
                # O header não vem com valor antes, então estimamos subtraindo 1
                remaining_str = response.headers.get("X-RateLimit-Remaining", "5000")
                rate_limit_after_first = int(remaining_str)
                rate_limit_before = rate_limit_after_first + 1  # Estimar o antes
                rate_limit_reset = response.headers.get("X-RateLimit-Reset")

            # Verificar rate limit durante execução
            remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
            if remaining < 200:
                print(f"REST rate limit baixo ({remaining}). Pausando por 60s...")
                time.sleep(60)

            if endpoint.startswith(f"/repos/{owner}/{repo}/pulls"):
                collected_data["pulls"] = response.json()

        # Requisições adicionais para reviews dos PRs (limitado aos 10 primeiros)
        if "pulls" in collected_data:
            for pr in collected_data["pulls"][
                :10
            ]:  # Limitar para evitar explosão de requests
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

        # Capturar rate limit DEPOIS de todas as requisições
        # Fazer uma requisição leve só para pegar o rate limit final
        final_check = requests.get(f"{BASE_URL}/rate_limit", headers=headers)
        if final_check.status_code == 200:
            rate_data = final_check.json()
            if "resources" in rate_data and "core" in rate_data["resources"]:
                rate_limit_after = rate_data["resources"]["core"]["remaining"]

        # Calcular consumo total
        rate_limit_consumed = None
        if rate_limit_before is not None and rate_limit_after is not None:
            rate_limit_consumed = rate_limit_before - rate_limit_after

        return {
            "repo": f"{owner}/{repo}",
            "api_type": "REST",
            "response_time_ms": total_time_ms,
            "response_size_bytes": total_size_bytes,
            "num_requests": num_requests,
            "rate_limit_before": rate_limit_before,
            "rate_limit_after": rate_limit_after,
            "rate_limit_consumed": rate_limit_consumed,
            "rate_limit_cost": None,  # REST não tem conceito de "cost" como GraphQL
            "rate_limit_reset_at": rate_limit_reset,
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
            "rate_limit_before": rate_limit_before,
            "rate_limit_after": rate_limit_after,
            "rate_limit_consumed": None,
            "rate_limit_cost": None,
            "rate_limit_reset_at": rate_limit_reset,
            "status": "error",
            "error_message": str(e),
        }
