"""침착의 Streamlit 진입점과 공통 화면 구성."""
import os
from pathlib import Path

# Support VS Code's "Run Python File" as well as `streamlit run app.py`.
if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        direct_run = get_script_run_ctx(suppress_warning=True) is None
    except ModuleNotFoundError as error:
        if error.name != "streamlit":
            raise
        direct_run = True

    if direct_run:
        app_path = Path(__file__).resolve()
        os.chdir(app_path.parent)
        if os.name == "nt":
            import subprocess

            raise SystemExit(subprocess.call(
                [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", "실행.bat"],
                cwd=app_path.parent,
            ))
        from launch import main
        raise SystemExit(main())

import streamlit as st

from services.parking_data import service_inventory
from services.parking_map import PREVIEW_LOCATION
from services.service_config import PARKING_DATA_VERSION, SERVICE_DISTRICTS
from services.ui import render_brand_bar, render_footer, render_service_summary, render_sidebar

st.set_page_config(
    page_title="침착 | 주차장 침수 위험도",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 카카오 길찾기(현재 비활성) 키는 코드에 적지 않고 환경 변수에서만 읽습니다.
st.session_state["_kakao_rest_api_key"] = os.environ.get("KAKAO_REST_API_KEY", "").strip()

if st.session_state.get("parking_dataset_version") != PARKING_DATA_VERSION:
    st.session_state.update(parking_dataset_version=PARKING_DATA_VERSION, compare_ids=[], selected_id=None, parking_district=SERVICE_DISTRICTS[0])
if "compare_ids" not in st.session_state:
    st.session_state["compare_ids"] = [1, 2]
if "selected_id" not in st.session_state:
    st.session_state["selected_id"] = None

# The same reference point drives search, detail, comparison, and distances.
# Temporary preview: 4 scored parking locations within 300m of Saekdong Park.
if st.session_state.get("preview_location_version") != "gangbuk-scored-parking-v3":
    st.session_state.update(
        preview_location_version="gangbuk-scored-parking-v3",
        current_location=PREVIEW_LOCATION,
        parking_view_request="nearby",
        selected_id=None,
    )

pages = [
    st.Page("pages/0_Home.py", title="홈 (주차장 탐색)", default=True),
    st.Page("pages/1_FAQ.py", title="FAQ", url_path="faq"),
    st.Page("pages/2_Analysis_Results.py", title="분석 데이터 결과", url_path="analysis-results"),
]
current_page = st.navigation(pages, position="hidden")

render_brand_bar()
render_service_summary(service_inventory())
render_sidebar(pages, current_page)
body = st.container()
render_footer()
with body:
    current_page.run()
