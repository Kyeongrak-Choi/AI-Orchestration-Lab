# DB 장애 테스트 — 진짜 DB를 끄지 않고, 연결 함수를 "항상 실패"로 바꿔 끼워 확인한다
from fastapi.testclient import TestClient

from app import history
from app.main import app

client = TestClient(app)


def broken_conn():
    raise ConnectionError("DB 장애 (실습용)")


def test_db_down_is_not_fatal(monkeypatch):
    monkeypatch.setattr(history, "get_conn", broken_conn)  # DB가 꺼진 상황을 흉내 낸다

    health = client.get("/health")
    assert health.status_code == 200  # 이력 DB는 비치명 → 재시작 대상이 아니다
    assert health.json()["status"] == "degraded"
    assert health.json()["checks"]["db"] is False

    # 핵심 기능(/check)은 DB 없이도 동작한다 (이력 저장 실패는 경고 로그로만 남는다)
    res = client.post("/check", json={"text": "짧은 글.", "name": "숲속 캠핑 의자", "price": "29,900원"})
    assert res.status_code == 200