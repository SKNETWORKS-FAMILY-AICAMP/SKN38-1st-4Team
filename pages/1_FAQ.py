"""서비스 이용과 위험 점수에 관한 자주 묻는 질문."""
import streamlit as st

from services.faq import load_faq

st.title("궁금한 점을 확인하세요.")
faq = load_faq()
categories = list(dict.fromkeys(entry.category for entry in faq))
category = st.radio("질문 카테고리", ["전체 질문", *categories], horizontal=True)
questions = [entry for entry in faq if category == "전체 질문" or entry.category == category]
st.subheader(f"자주 묻는 질문 {len(questions)}")
for category_name in categories:
    group = [entry for entry in questions if entry.category == category_name]
    if not group:
        continue
    st.subheader(f"{category_name} · {len(group)}개")
    for entry in group:
        with st.expander(f"Q. {entry.question}", expanded=entry == questions[0]):
            st.write(entry.answer)
