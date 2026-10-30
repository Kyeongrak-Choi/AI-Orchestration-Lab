# 이력 조회 — 운영자의 4가지 질문을 SQL로 답한다
# 실행: uv run python query_history.py   (이 폴더에서)
import sys

from app.history import get_conn

sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않게


def run(title, sql):
    print("=" * 56)
    print(title)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        for row in cur.fetchall():
            print(" ", row)


# Q1. 방금 무슨 일이 있었나 — 최근 요청 5건
run("Q1. 최근 요청 5건", """
    SELECT to_char(ts, 'HH24:MI:SS'), method, path, status, duration_ms
    FROM request_history ORDER BY ts DESC LIMIT 5
""")

# Q2. 서버 오류(5xx)는 언제, 왜 났나
run("Q2. 서버 오류 목록", """
    SELECT to_char(ts, 'HH24:MI:SS'), path, error
    FROM request_history WHERE status >= 500 ORDER BY ts DESC LIMIT 10
""")

# Q3. 어느 경로가 바쁘고 느린가
run("Q3. 경로별 요청 수·평균 지연", """
    SELECT path, count(*), round(avg(duration_ms)::numeric, 1)
    FROM request_history GROUP BY path ORDER BY count(*) DESC
""")

# Q4. 오늘 LLM에 얼마나 썼나
run("Q4. 오늘 토큰 사용량", """
    SELECT count(*), coalesce(sum(input_tokens), 0), coalesce(sum(output_tokens), 0)
    FROM llm_history WHERE ts::date = current_date
""")

# Q5. 최근 7일 LLM에 얼마나 썼나
run("Q5. 최근 일주일 토큰 사용량", """
    SELECT count(*), coalesce(sum(input_tokens), 0), coalesce(sum(output_tokens), 0)
    FROM llm_history WHERE ts::date between current_date -7 and current_date
""")