# 상품 소개문 서비스 v4 — Day 11: 실행 이력 DB 저장
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.checker import check_rules
from app.history import init_db, is_db_alive, save_llm_call, save_request
from app.logging_setup import setup_logger
from app.writer import write_intro

app = FastAPI(title="상품 소개문 서비스")
logger = setup_logger()
init_db()  # 서비스가 뜰 때 이력 테이블을 준비한다 (DB가 없어도 서비스는 뜬다)


# ---------- 요청 로그 미들웨어: 모든 요청이 지나가는 문 ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        # 처리되지 않은 예외 = 서버 장애(500) → ERROR로 기록하고 다시 던진다
        # 원칙: 모든 요청은 정확히 한 줄의 request 이벤트를 남긴다
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.error(
            "unhandled exception",
            extra={"data": {"event": "request", "method": request.method,
                            "path": request.url.path, "status": 500,
                            "error": str(exc), "duration_ms": duration_ms}},
        )
        save_request(request.method, request.url.path, 500, duration_ms, error=str(exc))
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    entry = {"event": "request", "method": request.method, "path": request.url.path,
             "status": response.status_code, "duration_ms": duration_ms}
    if response.status_code >= 500:
        logger.error("server error", extra={"data": entry})
    elif response.status_code >= 400:
        logger.warning("client error", extra={"data": entry})
    else:
        logger.info("", extra={"data": entry})
    # 로그(파일)와 이력(DB)을 함께 남긴다 — 파일은 진단용, DB는 조회·집계용
    save_request(request.method, request.url.path, response.status_code, duration_ms)
    return response


# ---------- 엔드포인트 ----------
class CheckRequest(BaseModel):
    text: str
    name: str
    price: str


class WriteRequest(BaseModel):
    name: str
    price: str
    feature: str


@app.get("/health")
def health():
    """심층 Health Check — "살아 있음"이 아니라 "일할 수 있음"을 점검한다.

    감시자(watchdog)·Docker HEALTHCHECK·로드밸런서가 이 응답을 보고 판단한다.
    """
    checks = {
        "api_key": bool(os.getenv("OPENAI_API_KEY")),          # LLM 호출 가능한가
        "logs_writable": os.access(Path("logs"), os.W_OK),      # 로그를 남길 수 있는가
        "db": is_db_alive(),                                    # 이력을 저장할 수 있는가
    }
    # 필수 항목이 깨지면 503 — 감시자가 재시작한다
    if not (checks["api_key"] and checks["logs_writable"]):
        return JSONResponse(status_code=503, content={"status": "down", "checks": checks})
    # DB는 이력용(비치명)이라 200 유지 — 앱을 재시작해도 DB는 고쳐지지 않는다 (Day 10 실측)
    if not checks["db"]:
        return JSONResponse(status_code=200, content={"status": "degraded", "checks": checks})
    return JSONResponse(status_code=200, content={"status": "ok", "checks": checks})


@app.post("/check")
def check(req: CheckRequest):
    violations = check_rules(req.text, {"name": req.name, "price": req.price})
    return {"passed": not violations, "violations": violations}


@app.post("/write")
def write(req: WriteRequest):
    """LLM 호출 엔드포인트 — 토큰 사용량(=비용)을 로그와 이력에 남긴다."""
    text, usage, duration, model = write_intro(req.name, req.price, req.feature)
    duration_ms = round(duration * 1000, 1)
    in_tok = usage.get("input_tokens", 0)
    out_tok = usage.get("output_tokens", 0)
    logger.info(
        "",
        extra={"data": {"event": "llm_call", "model": model,  # 대체 모델로 답했다면 그 이름이 남는다
                        "input_tokens": in_tok, "output_tokens": out_tok,
                        "duration_ms": duration_ms}},
    )
    save_llm_call(model, in_tok, out_tok, duration_ms)
    return {"text": text, "tokens": usage.get("total_tokens", 0), "model": model}


@app.get("/boom")
def boom():
    """의도된 장애 주입용 — 오류 로그 관찰과 Day 10(장애 감지) 실습에 쓴다."""
    raise RuntimeError("의도된 장애입니다 (실습용)")