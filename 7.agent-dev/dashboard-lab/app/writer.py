# LLM 작성자 — Day 10에서 만든 재시도(tenacity) + 대체 모델 (Day 11은 그대로 이어받는다)
import os
import time

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# 장애 주입: .env에 PRIMARY_MODEL=gpt-없는모델 을 넣고 서버를 다시 띄우면 주 모델이 계속 실패한다
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gpt-4o-mini")
BACKUP_MODEL = "gpt-5.4-nano"  # 대체 모델 — 2026-10-25 호출 확인 (gpt-4.1-nano는 단종돼 404). 더 싸고 작은 모델로 "품질을 조금 낮춰서라도 답한다"

# max_retries=0: 라이브러리 자체 재시도를 끈다 → 재시도 횟수를 tenacity 한 곳에서만 센다
primary = ChatOpenAI(model=PRIMARY_MODEL, temperature=0.9, max_retries=0)
backup = ChatOpenAI(model=BACKUP_MODEL, temperature=0.9, max_retries=0)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4), reraise=True)
def _invoke_primary(prompt):
    """주 모델: 일시 오류(네트워크·429 등)면 1→2초 간격으로 최대 3회 시도한다."""
    return primary.invoke(prompt)


def _invoke_with_fallback(prompt):
    """주 모델을 재시도하고, 끝내 실패하면 대체 모델로 한 번 부른다. 반환: (응답, 실제로 쓴 모델)"""
    try:
        return _invoke_primary(prompt), PRIMARY_MODEL
    except Exception:
        # 재시도로도 안 되면 지속 장애로 보고 대체 경로로 간다 (대체 모델도 실패하면 예외가 그대로 올라간다)
        return backup.invoke(prompt), BACKUP_MODEL


def write_intro(name, price, feature):
    """상품 소개문을 생성하고 (본문, 토큰 사용량, 소요 초, 쓴 모델)을 반환한다."""
    start = time.perf_counter()
    res, model = _invoke_with_fallback(
        f"당신은 쇼핑몰 상품 소개문 작성자입니다. 3문장으로 쓰고 소개문만 출력하세요.\n"
        f"제품명: {name} / 가격: {price} / 특징: {feature}"
    )
    duration = time.perf_counter() - start
    usage = res.usage_metadata or {}
    return res.content.strip(), usage, duration, model