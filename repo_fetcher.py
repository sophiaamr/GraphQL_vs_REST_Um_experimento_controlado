import requests
import time


def fetch_top_repositories(token: str, num_repos: int = 100, min_stars: int = 50000):
    """
    Busca os repositórios mais populares do GitHub dinamicamente.

    Args:
        token: GitHub personal access token
        num_repos: Quantidade de repositórios a buscar (máx 100)
        min_stars: Número mínimo de estrelas (padrão 50.000)

    Returns:
        Lista de strings no formato "owner/repo"
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    repositories = []
    per_page = 100  # Máximo permitido pela API

    # Buscar repositórios com >= min_stars, ordenados por estrelas
    query = f"stars:>={min_stars}"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={per_page}"

    try:
        print(f"Buscando top {num_repos} repositórios com >= {min_stars} estrelas...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        if "items" not in data:
            raise ValueError("Resposta da API não contém 'items'")

        for item in data["items"][:num_repos]:
            repo_full_name = item["full_name"]
            stars = item["stargazers_count"]
            repositories.append(repo_full_name)
            print(f"  - {repo_full_name} ({stars:,} ⭐)")

        print(f"\n✓ {len(repositories)} repositórios carregados com sucesso!\n")

        # Verificar rate limit
        remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
        if remaining < 100:
            print(f"⚠ Rate limit baixo: {remaining} requisições restantes")
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            if reset_time:
                wait_time = reset_time - time.time()
                if wait_time > 0:
                    print(f"Aguardando {wait_time:.0f}s para reset do rate limit...")
                    time.sleep(wait_time + 5)

        return repositories

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar repositórios: {e}")
        raise
