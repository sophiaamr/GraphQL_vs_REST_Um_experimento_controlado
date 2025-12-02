import os
import pandas as pd
import random
import time
from tqdm import tqdm
from dotenv import load_dotenv
import rest_collector
import graphql_collector
from repo_fetcher import fetch_top_repositories


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN não encontrado. Por favor, crie um .env")

# --- 1. CONFIGURAÇÕES DO EXPERIMENTO ---

# ⚙️ PARÂMETROS CONFIGURÁVEIS PARA EXECUÇÃO INCREMENTAL
NUM_REPOSITORIES = 100  # 🔧 ALTERE AQUI: 60, 70, 80, 90, 100 (fases do experimento)
MIN_STARS = 50000  # Critério: repositórios com >= 50.000 estrelas
PAUSE_INTERVAL_SEC = 1.5  # Intervalo entre requisições

OUTPUT_FILE = f"experiment_results_phase_{NUM_REPOSITORIES}.csv"


# --- 2. BUSCAR REPOSITÓRIOS DINAMICAMENTE ---


def get_repositories():
    """
    Busca os top repositórios dinamicamente da API do GitHub.
    Retorna a quantidade definida em NUM_REPOSITORIES.
    """
    print(
        f"📊 Configuração: {NUM_REPOSITORIES} repositórios, {MIN_STARS:,} estrelas mínimas"
    )
    print("=" * 70)

    repositories = fetch_top_repositories(
        token=GITHUB_TOKEN, num_repos=NUM_REPOSITORIES, min_stars=MIN_STARS
    )

    if len(repositories) < NUM_REPOSITORIES:
        print(
            f"⚠️ Aviso: Apenas {len(repositories)} repositórios encontrados (esperado: {NUM_REPOSITORIES})"
        )

    return repositories


def run_experiment():
    """
    Executa o experimento completo: GraphQL vs REST
    """
    # Buscar repositórios dinamicamente
    repositories = get_repositories()

    print(f"\n🔬 Iniciando experimento: GraphQL vs REST")
    print(f"Objetos: {len(repositories)} repositórios")
    print(f"Tratamentos: 2 (REST, GraphQL)")
    print(f"Total de medições: {len(repositories) * 2}")
    print("--------------------------------------------------")

    experiment_plan = []
    for repo_full in repositories:
        experiment_plan.append((repo_full, "REST"))
        experiment_plan.append((repo_full, "GraphQL"))

    # Randomizar a ordem de execução
    print("🔀 Randomizando ordem de execução...")
    random.shuffle(experiment_plan)

    results = []

    # Executar o plano
    for repo_full, api_type in tqdm(experiment_plan, desc="Executando medições"):
        owner, repo = repo_full.split("/")

        try:
            if api_type == "REST":
                result_data = rest_collector.fetch_rest_data(owner, repo, GITHUB_TOKEN)
            else:
                result_data = graphql_collector.fetch_graphql_data(
                    owner, repo, GITHUB_TOKEN
                )

            results.append(result_data)

        except Exception as e:
            print(f"Erro irrecuperável em {repo_full} ({api_type}): {e}")
            results.append(
                {
                    "repo": repo_full,
                    "api_type": api_type,
                    "status": "critical_error",
                    "error_message": str(e),
                }
            )

        time.sleep(PAUSE_INTERVAL_SEC)

    # --- 4. SALVAR RESULTADOS ---
    print("\n--------------------------------------------------")
    print("✅ Experimento concluído.")

    df = pd.DataFrame(results)

    # Salvar em CSV
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"💾 Resultados salvos em: {OUTPUT_FILE}")

    # Mostrar um resumo
    print("\n📊 Resumo dos Resultados (Médias):")
    df_success = df[df["status"] == "success"]
    if not df_success.empty:
        df_success["response_time_ms"] = pd.to_numeric(df_success["response_time_ms"])
        df_success["response_size_bytes"] = pd.to_numeric(
            df_success["response_size_bytes"]
        )
        df_success["num_requests"] = pd.to_numeric(df_success["num_requests"])

        print(
            df_success.groupby("api_type")[
                ["response_time_ms", "response_size_bytes", "num_requests"]
            ].mean()
        )

    errors = df[df["status"] != "success"]
    print(f"\n❌ Total de medições com falha: {len(errors)}")
    if not errors.empty:
        print(errors.groupby(["repo", "api_type"]).size())


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 EXPERIMENTO: GraphQL vs REST - API do GitHub")
    print("=" * 70)
    run_experiment()
    print("\n" + "=" * 70)
    print("🎉 Execução finalizada!")
    print("=" * 70)
