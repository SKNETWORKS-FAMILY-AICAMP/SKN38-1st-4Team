"""Inactive Kakao directions panel, retained for later restoration."""
import streamlit as st
import pydeck as pdk

def route_panel(row, lat, lon):
    from datetime import datetime
    from services.kakao_navi import directions, DirectionsError
    identifier = int(row["id"])
    st.markdown("#### 카카오 자동차 길찾기")
    st.caption("출발지: 강남역 · 목적지: 선택한 예시 좌표")
    priorities = {"추천 경로": "RECOMMEND", "최단 시간": "TIME", "최단 거리": "DISTANCE"}
    choice = st.selectbox("경로 옵션", list(priorities), key=f"route_option_{identifier}")
    signature = (float(lon), float(lat), float(row["lon"]), float(row["lat"]), priorities[choice])
    state_key = f"route_result_{identifier}"
    if st.button("자동차 경로 조회", key=f"route_button_{identifier}", use_container_width=True):
        st.session_state.pop(state_key, None)
        try:
            with st.spinner("카카오에서 자동차 경로를 조회하고 있습니다…"):
                result = directions(signature[:2], signature[2:4], signature[4])
            st.session_state[state_key] = (signature, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except DirectionsError as error:
            st.error(str(error))
    stored = st.session_state.get(state_key)
    if not stored or stored[0] != signature:
        return
    result, queried_at = stored[1], stored[2]
    st.metric("자동차 이동 거리", f'{result["distance"] / 1000:,.2f} km')
    st.metric("예상 소요 시간", f'{max(1, int((result["duration"] + 59) // 60)):,}분')
    if result["toll"] is not None:
        st.caption(f'예상 통행료 {result["toll"]:,}원')
    st.caption(f"조회 시각(서버): {queried_at} · 교통 상황에 따라 달라질 수 있습니다.")
    if result["paths"]:
        points = [point for road in result["paths"] for point in road["path"]]
        st.pydeck_chart(pdk.Deck(
            map_style="light", map_provider="carto",
            initial_view_state=pdk.data_utils.compute_view(points),
            layers=[pdk.Layer("PathLayer", data=result["paths"], get_path="path",
                              get_color=[8, 123, 255], get_width=5, width_units="pixels"),
                    pdk.Layer("ScatterplotLayer", data=[{"position": list(signature[:2])},
                              {"position": list(signature[2:4])}], get_position="position",
                              get_radius=28, get_fill_color=[6, 39, 92])],
        ), height=300, key=f"route_map_{identifier}")
    else:
        st.info("경로 요약만 반환되어 지도에 표시할 경로가 없습니다.")
    st.caption("경로 제공: 카카오모빌리티 · 앱 내 경로 조회이며 음성 길안내 기능은 제공하지 않습니다.")


