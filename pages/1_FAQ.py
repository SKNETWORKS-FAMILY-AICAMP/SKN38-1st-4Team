"""서비스 이용과 위험 점수에 관한 자주 묻는 질문."""
import streamlit as st

from services.faq import FAQ

st.title("궁금한 점을 확인하세요.")
category = st.radio("질문 카테고리", ["전체 질문", "위험지수", "서비스 이용", "데이터"], horizontal=True)
questions = [q for q in FAQ if category == "전체 질문" or q[0] == category]
st.subheader(f"자주 묻는 질문 {len(questions)}")
for index, (_, question, answer) in enumerate(questions):
    with st.expander(f"Q. {question}", expanded=index == 0):
        st.write(answer)
