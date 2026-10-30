# 대체 모델 테스트 — 진짜 LLM을 부르지 않고, 가짜 모델로 "주 모델 실패 → 대체 모델" 경로만 확인한다
import pytest
from tenacity import wait_none

from app import writer


class FakeResponse:
    content = "대체 모델이 쓴 소개문입니다."
    usage_metadata = {"total_tokens": 10}


class BrokenModel:
    """항상 실패하는 주 모델 (장애 흉내)"""

    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        raise RuntimeError("주 모델 장애 (실습용)")


class FlakyModel:
    """첫 호출만 실패하고 두 번째부터 성공하는 주 모델 (일시 오류 흉내)"""

    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("일시 오류 (실습용)")
        return FakeResponse()


class WorkingModel:
    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return FakeResponse()


@pytest.fixture
def no_wait(monkeypatch):
    """재시도 사이 대기(1초 → 2초)를 0초로 바꾼다. 테스트가 끝나면 원래대로 돌아온다."""
    monkeypatch.setattr(writer._invoke_primary.retry, "wait", wait_none())


def test_fallback_when_primary_fails(monkeypatch):
    # 대기 시간을 바꾸지 않은 원래 테스트 — 재시도 사이에 실제로 1초, 2초를 기다려 약 3초 걸린다
    broken = BrokenModel()
    monkeypatch.setattr(writer, "primary", broken)  # 주 모델을 고장 난 가짜로 바꿔 끼운다
    monkeypatch.setattr(writer, "backup", WorkingModel())

    text, usage, duration, model = writer.write_intro("숲속 캠핑 의자", "29,900원", "가벼움")

    assert broken.calls == 3  # 재시도 3번을 다 쓰고
    assert model == writer.BACKUP_MODEL  # 대체 모델로 답했다
    assert text == "대체 모델이 쓴 소개문입니다."


def test_fallback_without_wait(monkeypatch, no_wait):
    # 위와 같은 경로를 대기 0초로 — 재시도 횟수와 결과는 같고 시간만 줄어든다
    broken = BrokenModel()
    monkeypatch.setattr(writer, "primary", broken)
    monkeypatch.setattr(writer, "backup", WorkingModel())

    text, usage, duration, model = writer.write_intro("숲속 캠핑 의자", "29,900원", "가벼움")

    assert broken.calls == 3
    assert model == writer.BACKUP_MODEL
    assert duration < 1  # 대기가 없으므로 1초 안에 끝난다


def test_retry_succeeds_on_second_try(monkeypatch, no_wait):
    # 일시 오류는 재시도가 해결한다 — 대체 모델까지 가지 않는다
    flaky = FlakyModel()
    backup = WorkingModel()
    monkeypatch.setattr(writer, "primary", flaky)
    monkeypatch.setattr(writer, "backup", backup)

    text, usage, duration, model = writer.write_intro("숲속 캠핑 의자", "29,900원", "가벼움")

    assert flaky.calls == 2  # 한 번 실패, 두 번째에 성공
    assert model == writer.PRIMARY_MODEL  # 주 모델이 답했다
    assert backup.calls == 0  # 대체 모델은 부르지 않았다