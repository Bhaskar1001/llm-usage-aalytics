
import sqlite3
from pathlib import Path

from src.analytics import (
    load_usage,
    summarize_usage,
    usage_by_model,
    usage_by_user,
)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "llm_usage.csv"
DB_PATH = ROOT / "data" / "analytics.db"

df = load_usage(DATA_PATH)

print("\n=== Overall Metrics ===")
for metric, value in summarize_usage(df).items():
    print(f"{metric}: {value:.2f}" if isinstance(value, float)
          else f"{metric}: {value}")

print("\n=== Usage by Model ===")
print(usage_by_model(df).to_string(index=False))

print("\n=== Usage by User ===")
print(usage_by_user(df).to_string(index=False))

with sqlite3.connect(DB_PATH) as connection:
    df.to_sql("llm_usage", connection, if_exists="replace", index=False)

    query = """
        SELECT
            model,
            COUNT(*) AS requests,
            SUM(total_tokens) AS total_tokens,
            ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
            SUM(estimated_cost_usd) AS estimated_cost_usd
        FROM llm_usage
        GROUP BY model
        ORDER BY total_tokens DESC;
    """

    print("\n=== SQL Results ===")
    print(connection.execute(query).fetchall())
