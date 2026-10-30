# API 테스트 — 서버를 띄우지 않고 프로세스 안에서 검사한다 (TestClient)
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_deep():
    """심층 Health Check: 상태와 점검 항목을 함께 반환한다."""
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["checks"]["api_key"] is True
    assert body["checks"]["logs_writable"] is True


def test_health_down_without_api_key(monkeypatch):
    """키가 없으면 LLM을 못 부른다 → 치명 → 503 + down (DB만 꺼졌을 때의 200 + degraded와 다르다)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)  # 이 테스트 동안만 키를 없앤다
    res = client.get("/health")
    assert res.status_code == 503
    body = res.json()
    assert body["status"] == "down"
    assert body["checks"]["api_key"] is False


def test_check_endpoint():
    res = client.post(
        "/check",
        json={
            "text": "숲속 캠핑 의자는 가볍습니다. 컵홀더가 있으며 가격은 29,900원입니다. 지금 만나보세요.",
            "name": "숲속 캠핑 의자",
            "price": "29,900원",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["passed"] is True
    assert body["violations"] == []