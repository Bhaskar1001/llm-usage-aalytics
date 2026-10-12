
from pathlib import Path

import numpy as np
import pandas as pd


def load_usage(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    numeric_columns = [
        "prompt_tokens",
        "completion_tokens",
        "latency_ms",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=["request_id", "timestamp", "model", *numeric_columns]
    ).drop_duplicates(subset=["request_id"])

    df["total_tokens"] = (
        df["prompt_tokens"] + df["completion_tokens"]
    ).astype(int)

    df["latency_ms"] = df["latency_ms"].astype(int)
    df["date"] = df["timestamp"].dt.date

    # Illustrative rates only; replace with your provider's pricing.
    rates = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gemma": {"input": 0.0, "output": 0.0},
    }

    df["estimated_cost_usd"] = [
        (
            row.prompt_tokens * rates.get(row.model, {"input": 0, "output": 0})["input"]
            + row.completion_tokens * rates.get(row.model, {"input": 0, "output": 0})["output"]
        ) / 1_000_000
        for row in df.itertuples()
    ]

    return df


def summarize_usage(df: pd.DataFrame) -> dict:
    return {
        "total_requests": len(df),
        "total_tokens": int(df["total_tokens"].sum()),
        "average_latency_ms": float(df["latency_ms"].mean()),
        "success_rate_pct": float(
            np.mean(df["status"].eq("success")) * 100
        ),
        "failure_rate_pct": float(
            np.mean(df["status"].eq("failure")) * 100
        ),
        "estimated_cost_usd": float(df["estimated_cost_usd"].sum()),
    }


def usage_by_model(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("model")
        .agg(
            requests=("request_id", "count"),
            total_tokens=("total_tokens", "sum"),
            average_latency_ms=("latency_ms", "mean"),
            estimated_cost_usd=("estimated_cost_usd", "sum"),
        )
        .reset_index()
    )


def usage_by_user(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("user_id")
        .agg(
            requests=("request_id", "count"),
            total_tokens=("total_tokens", "sum"),
        )
        .sort_values("total_tokens", ascending=False)
        .reset_index()
    )
