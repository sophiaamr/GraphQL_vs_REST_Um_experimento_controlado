import os
import pandas as pd
import random
import time
from tqdm import tqdm
from dotenv import load_dotenv
import rest_collector
import graphql_collector


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN não encontrado. Por favor, crie um .env")

# --- 1. OBJETOS EXPERIMENTAIS ---

REPOSITORIES = ["facebook/react"]

# --- 2. PROJETO EXPERIMENTAL ---
REPETITIONS = 10
OUTPUT_FILE = "experiment_results.csv"
PAUSE_INTERVAL_SEC = 1.5


def run_experiment():
    print(f"Iniciando experimento: GraphQL vs REST")
    print(f"Objetos: {len(REPOSITORIES)} repositórios")
    print(f"Tratamentos: 2 (REST, GraphQL)")
    print(f"Repetições: {REPETITIONS}")
    print(f"Total de medições: {len(REPOSITORIES) * 2 * REPETITIONS}")
    print("--------------------------------------------------")

    experiment_plan = []
    for _ in range(REPETITIONS):
        for repo_full in REPOSITORIES:
            experiment_plan.append((repo_full, "REST"))
            experiment_plan.append((repo_full, "GraphQL"))

    # Randomizar a ordem de execução

    print("Randomizando ordem de execução...")
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
    print("Experimento concluído.")

    df = pd.DataFrame(results)

    # Salvar em CSV
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"Resultados salvos em: {OUTPUT_FILE}")

    # Mostrar um resumo
    print("\nResumo dos Resultados (Médias):")
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
    print(f"\nTotal de medições com falha: {len(errors)}")
    if not errors.empty:
        print(errors.groupby(["repo", "api_type"]).size())


if __name__ == "__main__":
    run_experiment()
