import streamlit as st
from openai import OpenAI

# 제목 및 설명
st.title("💬 yun's 월급 관리 Chatbot")
st.write(
    "yun's 월급 관리 Chatbot은 월급과 목표 저축 금액을 기반으로 개인 맞춤형 재정 계획을 제시하고, "
    "지출 항목을 하나씩 수정하면서 함께 조정해 나가는 대화형 챗봇입니다.\n"
    "이 앱을 사용하려면 OpenAI API 키가 필요합니다."
)

# OpenAI API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("계속하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    # 초기 계획 입력 폼 (한 번만 입력)
    if not st.session_state.initialized:
        with st.form("salary_plan_form"):
            salary = st.number_input("월급 (만원)", min_value=0)
            goal_amount = st.number_input("목표 금액 (만원)", min_value=0)
            years = st.number_input("몇 년 안에 모으고 싶은가요?", min_value=1)
            submitted = st.form_submit_button("계획 요청")

        if submitted:
            # 영어 프롬프트 생성
            prompt = (
                f"My monthly salary is {salary}만원. I want to save {goal_amount}만원 in {years} years. "
                "Please create a detailed savings and spending plan in Korean. Include budget allocation by category, "
                "saving strategy, and any advice to reach the goal. Continue speaking in Korean."
            )

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"월급: {salary}만원 / 목표: {goal_amount}만원 / 기간: {years}년")

            # 응답 생성
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                stream=True,
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.initialized = True

    # 초기화 이후에는 대화 지속
    else:
        # 이전 대화 출력
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 사용자 입력 받기
        if prompt := st.chat_input("예: 식비를 30만원으로 바꾸고 싶어요"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 영어 시스템 메시지 추가 (한글 응답 유지)
            system_message = {
                "role": "system",
                "content": (
                    "You are a financial assistant chatbot. Continue the conversation in Korean, "
                    "adjusting the budget based on the user's requests, and helping them achieve their savings goal."
                )
            }

            # 챗 응답 생성
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[system_message] + st.session_state.messages,
                stream=True,
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
