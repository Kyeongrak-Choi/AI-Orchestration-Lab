# 대시보드 데이터 계층 — 화면(UI)과 분리해 두면 테스트·재사용이 쉽다
import pandas as pd

from app.history import get_conn

# 예시 단가 (USD / 100만 토큰) — 최신 요금표를 확인해 갱신한다
PRICE_INPUT = 0.15
PRICE_OUTPUT = 0.60


def _read(sql):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def load_requests():
    return _read("SELECT ts, method, path, status, duration_ms, error FROM request_history ORDER BY ts")


def load_llm():
    return _read("SELECT ts, model, input_tokens, output_tokens, duration_ms FROM llm_history ORDER BY ts")


def summary(req_df, llm_df):
    """지표 카드 4종의 값을 계산한다."""
    total = len(req_df)
    errors = int((req_df["status"] >= 500).sum()) if total else 0
    cost = (
        llm_df["input_tokens"].sum() / 1_000_000 * PRICE_INPUT
        + llm_df["output_tokens"].sum() / 1_000_000 * PRICE_OUTPUT
    ) if len(llm_df) else 0.0
    return {
        "total": total,
        "error_rate": (errors / total * 100) if total else 0.0,
        "avg_ms": float(req_df["duration_ms"].mean()) if total else 0.0,
        "cost_usd": float(cost),
    }


def requests_per_minute(req_df):
    """분 단위 요청 수 — 시간대별 추이 차트의 재료."""
    df = req_df.copy()
    df["minute"] = pd.to_datetime(df["ts"]).dt.floor("min")
    return df.groupby("minute").size().rename("요청 수")


def latency_by_path(req_df):
    return req_df.groupby("path")["duration_ms"].mean().round(1).rename("평균 지연(ms)")


def recent_errors(req_df, n=20):
    err = req_df[req_df["status"] >= 500].sort_values("ts", ascending=False).head(n)
    return err[["ts", "path", "error"]]