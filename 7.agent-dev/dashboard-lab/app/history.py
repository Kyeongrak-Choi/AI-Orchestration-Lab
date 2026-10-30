# 실행 이력 저장 — 로그는 파일에, 이력은 DB에 (조회·집계·대시보드의 재료)
import logging
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("service")


def get_conn():
    """DB 연결을 새로 연다.

    연결을 붙잡아 두지 않고 매번 새로 연다 → DB가 잠깐 꺼졌다 돌아오면 다음 호출부터 저절로 다시 붙는다 (재연결).
    connect_timeout: DB가 꺼져 있을 때 요청이 오래 멈추지 않게 2초에서 포기한다.
    """
    return psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=2)


def is_db_alive():
    """DB에 붙어서 간단한 질의가 되는지 본다 (/health의 db 항목)."""
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception:
        return False


def init_db():
    """이력 테이블 2개를 만든다 (있으면 그대로 둔다).

    DB가 아직 안 떴어도 서비스는 뜬다 (비치명 원칙) → 경고만 남긴다. 테이블이 없으면 이후 저장이 경고로 남는다.
    """
    try:
        _create_tables()
    except Exception as exc:
        logger.warning("", extra={"data": {"event": "init_db_failed", "error": str(exc)}})


def _create_tables():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS request_history (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMPTZ DEFAULT now(),
                method TEXT,
                path TEXT,
                status INT,
                duration_ms REAL,
                error TEXT
            );
            CREATE TABLE IF NOT EXISTS llm_history (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMPTZ DEFAULT now(),
                model TEXT,
                input_tokens INT,
                output_tokens INT,
                duration_ms REAL
            );
            """
        )


def save_request(method, path, status, duration_ms, error=None):
    """요청 이력 한 건을 저장한다.

    원칙: 이력 저장 실패가 서비스를 죽이면 안 된다 → 예외는 삼키고 경고만 남긴다.
    """
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO request_history (method, path, status, duration_ms, error) "
                "VALUES (%s, %s, %s, %s, %s)",
                (method, path, status, duration_ms, error),
            )
    except Exception as exc:
        logger.warning("", extra={"data": {"event": "history_save_failed", "error": str(exc)}})


def save_llm_call(model, input_tokens, output_tokens, duration_ms):
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO llm_history (model, input_tokens, output_tokens, duration_ms) "
                "VALUES (%s, %s, %s, %s)",
                (model, input_tokens, output_tokens, duration_ms),
            )
    except Exception as exc:
        logger.warning("", extra={"data": {"event": "history_save_failed", "error": str(exc)}})