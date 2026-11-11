"""세 화면에서 공통으로 사용하는 브랜드, 메뉴와 안내."""
from pathlib import Path

import streamlit as st

from services.risk_model import NOTE
from services.service_config import SERVICE_AREA, SERVICE_DISTRICTS

LOGO = str(Path(__file__).resolve().parents[1] / "assets" / "logo_main.png")


def render_brand_bar():
    brand_logo, brand_text = st.columns([1, 3], vertical_alignment="center")
    brand_logo.image(LOGO, width=138)
    brand_text.caption("침수 위험을 살피는 주차 습관")
    st.divider()


def render_service_summary(frame):
    st.caption(f'서비스 지역 {len(SERVICE_DISTRICTS)}개 구({SERVICE_AREA}) · 추정 위험점수 산정 주차장 {len(frame):,}개')
    st.caption("강수 자료가 있는 구부터 서비스합니다. 내 주변 또는 구별 보기로 확인하세요.")


def render_sidebar(pages, current):
    with st.sidebar:
        st.image(LOGO, width=170)
        st.caption("침수 위험을 살피는 주차 습관")
        for page in pages:
            is_current = page.url_path == current.url_path
            if st.button(
                page.title,
                key=f"nav_{page.title}",
                width="stretch",
                type="primary" if is_current else "secondary",
            ) and not is_current:
                st.switch_page(page)
        st.divider()
        st.caption(NOTE)


def render_footer():
    st.divider()
    foot_left, foot_right = st.columns(2)
    foot_left.markdown("**침착**  \n:gray[침수 위험을 살피는 주차 습관]")
    foot_right.caption("제공된 서울시 주차장 데이터 기반  \nCSV의 상대 침수 위험지수 · 실시간 침수 예측이 아닙니다.")


DATA_SOURCES = """
| 데이터 | 제공 기관 | 활용 목적 |
| --- | --- | --- |
| 전국주차장표준데이터 | 지방자치단체 | 서울시 내 주차장 데이터 수집 |
| 침수흔적도 | 행정안전부 재난보험과 | 과거 침수 이력 및 침수심 분석 |
| 방재기상관측(AWS) | 기상청 | 주차장 주변 강수 위험도 산출 |
| 서울시 경사도 | 도시공간본부 도시계획상임기획과 | 지형 특성을 활용한 저지대 위험도 분석 |
"""

ANALYSIS_SCOPE = """
| 구분 | 규모 / 범위 |
| --- | --- |
| 수집·분석 주차장 | **806곳** |
| 과거 침수구역 | **1,132곳** |
| 과거 침수구역 대표 위치에서 1km 이내 주차장 | **204곳** |
| 강수 위험도 분석 대상 5개 자치구 내 주차장 | **163곳** |
| **두 조건을 모두 만족하는 최종 분석 주차장** | **137곳** |
| 강수량 기준 기간 | **2025년** |
| 강수 분석 지역 | **은평구 · 강서구 · 서대문구 · 도봉구 · 강북구** |
"""

# 종합 위험지수 가중치: (이름, 가중치, 점 색상)
RISK_WEIGHTS = (
    ("강수 위험도", 0.30, "#7cc4ff"),
    ("저지대 위험도", 0.25, "#2f8ae6"),
    ("과거 침수 이력 위험도", 0.45, "#0b3f86"),
)


def render_data_sources():
    """데이터 출처 탭: 데이터 / 제공 기관 / 활용 목적 표."""
    st.markdown(DATA_SOURCES)


def _formula_html():
    plus = '<span aria-hidden="true" style="align-self:center;font-size:20px;color:#5b7190">+</span>'
    cards = []
    for name, weight, color in RISK_WEIGHTS:
        cards.append(
            f'<div style="flex:{weight * 100:g} 1 120px;min-width:0;padding:12px 14px;border-radius:8px;'
            f'background:#ffffff;border:1px solid #cfdff0;display:flex;flex-direction:column;gap:2px">'
            f'<span style="display:flex;align-items:center;gap:6px;font-size:14px;color:#3f5878">'
            f'<span style="width:10px;height:10px;border-radius:50%;background:{color};flex:none"></span>{name}</span>'
            f'<span style="font-size:28px;font-weight:700;line-height:1.3;color:#173e68">{weight:.0%}</span>'
            f'<span style="font-size:13px;color:#5b7190">× {weight:.2f}</span></div>'
        )
    bar = "".join(f'<div style="flex:{weight * 100:g};background:{color}"></div>' for _, weight, color in RISK_WEIGHTS)
    label = " + ".join(f"{name} × {weight:.2f}" for name, weight, _ in RISK_WEIGHTS)
    return (
        f'<figure aria-label="종합 위험지수 = {label}" style="margin:0;padding:20px;border-radius:8px;'
        'border:1px solid #cfdff0;background:#f5f9fd;display:flex;flex-direction:column;gap:16px;word-break:keep-all">'
        '<p style="margin:0;font-size:18px;font-weight:700;color:#173e68">종합 위험지수 '
        '<span style="font-weight:400;color:#5b7190">=</span></p>'
        f'<div style="display:flex;flex-wrap:wrap;align-items:stretch;gap:8px">{plus.join(cards)}</div>'
        f'<div style="display:flex;height:10px;border-radius:5px;overflow:hidden;gap:2px">{bar}</div>'
        '<figcaption style="font-size:13px;color:#5b7190">각 지표(0~100점)에 가중치를 곱해 더한 값입니다. '
        '막대 길이는 가중치 비율입니다.</figcaption></figure>'
    )


def render_reference_metrics():
    """참고 지표 탭: 분석 규모 표 아래에 종합 위험지수 공식."""
    st.markdown(ANALYSIS_SCOPE)
    st.html(_formula_html())
