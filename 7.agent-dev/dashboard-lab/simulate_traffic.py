# 모의 트래픽 생성기 — 하루치 운영을 몇 분으로 압축한다
# 실행: uv run python simulate_traffic.py   (이 폴더에서)
import random
import sys

from fastapi.testclient import TestClient

from app.main import app

sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔(cp949)에서 한글·기호 출력이 깨지지 않게

# raise_server_exceptions=False: 서버 예외를 500 응답으로 받는다 (실서버와 동일)
client = TestClient(app, raise_server_exceptions=False)

GOOD_TEXT = (
    "숲속 캠핑 의자는 가벼워서 휴대하기 편합니다. "
    "접이식 디자인과 컵홀더를 갖췄으며 가격은 29,900원입니다. 지금 만나보세요."
)
BAD_TEXT = "숲속 캠핑 의자는 혁신적입니다! 최고예요."

PRODUCT = {"name": "숲속 캠핑 의자", "price": "29,900원"}

requests_plan = (
    [("GET", "/health", None)] * 10
    + [("POST", "/check", {"text": GOOD_TEXT, **PRODUCT})] * 20
    + [("POST", "/check", {"text": BAD_TEXT, **PRODUCT})] * 10
    + [("POST", "/check", {"text": GOOD_TEXT})] * 5          # 필드 누락 → 422
    + [("GET", "/no-such-page", None)] * 3                    # 없는 주소 → 404
    + [("GET", "/boom", None)] * 3                            # 의도된 장애 → 500
    + [("POST", "/write", {"name": "숲속 캠핑 의자", "price": "29,900원",
                            "feature": "무게 900g, 접이식, 컵홀더"})] * 5  # LLM 호출
)

random.shuffle(requests_plan)

counts = {}
for method, path, body in requests_plan:
    if method == "GET":
        res = client.get(path)
    else:
        res = client.post(path, json=body)
    counts[res.status_code] = counts.get(res.status_code, 0) + 1

print(f"총 {len(requests_plan)}건 전송 완료. 상태 코드 분포: {dict(sorted(counts.items()))}")
print("→ 로그 파일과 DB 이력(request_history, llm_history)이 쌓였습니다. query_history.py와 dashboard.py로 확인하세요.")