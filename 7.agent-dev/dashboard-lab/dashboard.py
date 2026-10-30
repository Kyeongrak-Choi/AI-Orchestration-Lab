# 운영 대시보드 — 실행: uv run streamlit run dashboard.py   (이 폴더에서)
import streamlit as st

from dashboard_data import (
    latency_by_path,
    load_llm,
    load_requests,
    recent_errors,
    requests_per_minute,
    summary,
)

st.set_page_config(page_title="상품 소개문 서비스 — 운영 대시보드", layout="wide")
st.title("상품 소개문 서비스 — 운영 대시보드")


@st.cache_data(ttl=5)  # 5초마다 새 데이터 (새로고침하면 최신)
def load():
    return load_requests(), load_llm()


req_df, llm_df = load()

if req_df.empty:
    st.warning("이력이 없습니다. simulate_traffic.py로 트래픽을 만들어 주세요.")
    st.stop()

# ---------- 1. 지표 카드: 운영자의 첫 질문 4개 ----------
s = summary(req_df, llm_df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("총 요청", f"{s['total']}건")
c2.metric("서버 오류율", f"{s['error_rate']:.1f}%")
c3.metric("평균 지연", f"{s['avg_ms']:.1f}ms")
c4.metric("LLM 비용(추정)", f"${s['cost_usd']:.4f}")
c5.metric("최근 일주일 LLM 비용(추정)", f"${s['cost_usd']:.4f}")

# ---------- 2. 시간대별 추이 ----------
st.subheader("분 단위 요청 수")
st.line_chart(requests_per_minute(req_df))

# ---------- 3. 경로별 지연 ----------
st.subheader("경로별 평균 지연(ms)")
st.bar_chart(latency_by_path(req_df))

# ---------- 4. 최근 오류 ----------
st.subheader("최근 서버 오류")
err = recent_errors(req_df)
if err.empty:
    st.info("서버 오류 없음")
else:
    st.dataframe(err, width="stretch")  # 화면 폭에 맞춘다 (use_container_width는 폐기 예정)