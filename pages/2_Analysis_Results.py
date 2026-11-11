"""서비스 지역 주차장의 위험 등급, 점수 분포와 순위."""
import altair as alt
import pandas as pd
import streamlit as st

from services.parking_data import service_inventory
from services.parking_marker import COLORS, RISK_BANDS, risk_band
from services.risk_model import NOTE
from services.service_config import SERVICE_AREA

frame = service_inventory()
frame["level"] = frame["score"].map(lambda score: risk_band(score)[1])

st.title("데이터로 살펴보는 침수 위험")
st.info(NOTE)
st.caption(f"전체 통계는 검색 반경과 무관하게 서비스 지역({SERVICE_AREA})의 추정 위험점수 산정 주차장 {len(frame):,}개를 기준으로 집계합니다.")
counts = frame["level"].value_counts().reindex([band[1] for band in RISK_BANDS], fill_value=0)
metrics = [("분석 대상 주차장", len(frame))] + [(f"상대 위험도 {name}", counts[name]) for name in reversed(counts.index)]
for offset in range(0, len(metrics), 3):
    for col, (label, count) in zip(st.columns(3), metrics[offset:offset + 3]):
        col.metric(label, f"{count}개")
left, right = st.columns(2)
color = alt.Color("등급:N", scale=alt.Scale(domain=list(counts.index), range=[COLORS[name] for name in counts.index]), sort=list(counts.index))
with left:
    st.subheader("위험 등급별 분포")
    chart_data = pd.DataFrame({"등급": counts.index, "주차장 수": counts.values})
    st.altair_chart(alt.Chart(chart_data).mark_arc(innerRadius=70).encode(theta="주차장 수:Q", color=color, tooltip=["등급:N", "주차장 수:Q"]), width="stretch")
with right:
    st.subheader("위험지수 구간별 분포")
    bins = frame["score"].dropna().map(lambda value: risk_band(value)[4])  # 등급 배지와 같은 기준(위험지수의 정수 부분)
    distribution = bins.value_counts().reindex([band[4] for band in RISK_BANDS], fill_value=0)
    chart_data = pd.DataFrame({"점수 구간": distribution.index.astype(str), "주차장 수": distribution.values})
    st.altair_chart(alt.Chart(chart_data).mark_bar(color="#1685ff", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(x=alt.X("점수 구간:N", sort=None), y=alt.Y("주차장 수:Q", axis=alt.Axis(tickMinStep=1)), tooltip=["점수 구간:N", "주차장 수:Q"]), width="stretch")
for col, ascending in zip(st.columns(2), [False, True]):
    with col:
        st.subheader("위험지수 하위 주차장" if ascending else "위험지수 상위 주차장")
        ranking = frame.dropna(subset=["score"]).sort_values("score", ascending=ascending).head(3)
        if ranking.empty:
            st.info("위험점수가 연결되면 순위를 표시합니다.")
        st.dataframe(ranking[["name", "address", "score", "level"]].rename(columns={"name": "주차장", "address": "주소", "score": "위험지수", "level": "상대 등급"}), hide_index=True, width="stretch")
st.caption("예시 5등급: 매우 낮음 0–19 / 낮음 20–39 / 보통 40–59 / 높음 60–79 / 매우 높음 80–100. 실제 분석 기준 확정 시 변경될 수 있습니다.")
