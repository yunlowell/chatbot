import streamlit as st
from openai import OpenAI

# 제목 및 설명
st.title("💬 yun's 월급 관리 Chatbot")
st.write(
    "yun's 월급 관리 Chatbot은 OpenAI의 GPT 모델을 활용하여 월급과 목표 저축 계획을 바탕으로 "
    "효율적인 월급 관리 방법을 제안해주는 챗봇입니다.\n"
    "이 앱을 사용하려면 OpenAI API 키가 필요합니다."
)

# OpenAI API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("계속하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)

    # 입력 폼
    with st.form("salary_plan_form"):
        salary = st.number_input("월급 (만원)", min_value=0)
        goal_amount = st.number_input("목표 금액 (만원)", min_value=0)
        years = st.number_input("몇 년 안에 모으고 싶은가요?", min_value=1)
        submitted = st.form_submit_button("계획 요청")

    # 챗 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 요청이 제출되었을 경우
    if submitted:
        # 영어 프롬프트 생성
        prompt = (
            f"My monthly salary is {salary}만원. I want to save {goal_amount}만원 in {years} years. "
            "Please provide a detailed financial plan in Korean, including monthly savings goals, "
            "budgeting tips, and spending recommendations tailored to help me reach my goal."
        )

        # 사용자 메시지 저장 및 출력
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"월급: {salary}만원 / 목표: {goal_amount}만원 / 기간: {years}년")

        # 응답 생성
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # 응답 출력 및 저장
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
