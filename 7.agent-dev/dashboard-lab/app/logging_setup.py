# JSON 구조화 로거 — 한 줄 = JSON 하나 (기계가 집계할 수 있는 로그)
import json
import logging
from pathlib import Path

LOG_DIR = Path("logs")


class JsonFormatter(logging.Formatter):
    """로그 한 건을 JSON 한 줄로 만든다."""

    def format(self, record):
        entry = {
            "ts": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
        }
        # logger.info("...", extra={"data": {...}}) 로 넘긴 필드를 합친다
        entry.update(getattr(record, "data", {}))
        if record.getMessage():
            entry["message"] = record.getMessage()
        return json.dumps(entry, ensure_ascii=False)


def setup_logger():
    """서비스 로거: 전체는 service.log, 오류(ERROR)만 errors.log에 분리 기록."""
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("service")
    if logger.handlers:  # 중복 등록 방지 (재실행 대비)
        return logger
    logger.setLevel(logging.INFO)

    all_handler = logging.FileHandler(LOG_DIR / "service.log", encoding="utf-8")
    all_handler.setFormatter(JsonFormatter())
    logger.addHandler(all_handler)

    err_handler = logging.FileHandler(LOG_DIR / "errors.log", encoding="utf-8")
    err_handler.setLevel(logging.ERROR)  # ERROR 이상만 이 파일로
    err_handler.setFormatter(JsonFormatter())
    logger.addHandler(err_handler)
    return logger