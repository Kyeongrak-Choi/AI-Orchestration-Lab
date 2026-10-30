# 검사기 단위 테스트 — CI가 매 푸시마다 실행한다 (LLM 호출 없음: 빠르고 공짜)
from app.checker import check_rules

PRODUCT = {"name": "숲속 캠핑 의자", "price": "29,900원"}

GOOD_TEXT = (
    "숲속 캠핑 의자는 가벼워서 휴대하기 편합니다. "
    "접이식 디자인과 컵홀더를 갖췄으며 가격은 29,900원입니다. "
    "지금 만나보세요."
)


def test_correct_text_passes():
    assert check_rules(GOOD_TEXT, PRODUCT) == []


def test_missing_price_detected():
    text = GOOD_TEXT.replace(" 가격은 29,900원입니다.", "니다.")
    violations = check_rules(text, PRODUCT)
    assert any("R3" in v for v in violations)


def test_banned_word_detected():
    text = GOOD_TEXT.replace("가벼워서", "혁신적으로 가벼워서")
    violations = check_rules(text, PRODUCT)
    assert any("R4" in v for v in violations)