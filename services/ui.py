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
