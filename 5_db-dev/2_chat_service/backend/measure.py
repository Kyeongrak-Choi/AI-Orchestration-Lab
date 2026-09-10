import hashlib
import json
import sys
import time
import urllib.request

from app.redis_client import r

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjMyYjFmNjI5LWFlM2MtNGM0My1hMWQ4LWJkNDMzNGMzNmQzZCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2drcm5rcmhjenprem5ya29pdG1uLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyZTcyZmE1NC01YjQ5LTQyMzUtODhhNy1kODE0NDNmYWI4ZDUiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzg3ODE2Mjk5LCJpYXQiOjE3ODc4MTI2OTksImVtYWlsIjoiYUBhLmEiLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiYUBhLmEiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiIyZTcyZmE1NC01YjQ5LTQyMzUtODhhNy1kODE0NDNmYWI4ZDUifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc4NzgxMjY5OX1dLCJzZXNzaW9uX2lkIjoiZTRjYTM0NmYtNjQzNi00OGNlLWEzMzktN2U1NTVmZTcwOGU1IiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.83iXHFsktvVEyrBYzdcH1BuvqKUTsNf2icKXyM1UtQwcyHKLSDhliToa0srpi5-DoXEzOC1rDgVK0w4QruVWrA"
CONVERSATION_ID = "ba83e8eb-1d27-43d0-a406-aab7c2b8260a"


def call(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", "Bearer " + TOKEN)
    started = time.perf_counter()
    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read())
    return body, (time.perf_counter() - started) * 1000


def measure(path, cache_key, times=3):
    """캐시를 비우고 같은 요청을 여러 번 보낸다."""
    r.delete(cache_key)  # 1회차가 확실히 MISS 가 되게 한다
    print(f"\n{path}")
    for i in range(1, times + 1):
        body, ms = call(path)
        count = len(body) if isinstance(body, list) else "-"
        print(f"  {i}회차  {ms:7.1f} ms  {count}건  남은 TTL {r.ttl(cache_key):>4}s")


measure("/me", "session:" + hashlib.sha256(TOKEN.encode()).hexdigest())
measure(f"/conversations/{CONVERSATION_ID}/messages", f"messages:{CONVERSATION_ID}")
