import streamlit as st
from openai import OpenAI

# 타이틀 및 설명
st.title("💬 yun's 월급 관리 Chatbot")
st.write(
    "yun's 월급 관리 Chatbot은 월급과 저축 목표를 바탕으로 "
    "저축, 식비, 주거비, 교통비, 보험, 쇼핑 항목을 포함한 예산 계획을 세우고, "
    "지출 항목을 조정해가며 함께 관리해 나가는 챗봇입니다.\n"
    "이 앱을 사용하려면 OpenAI API 키가 필요합니다."
)

# OpenAI API Key 입력
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

    if "system_added" not in st.session_state:
        st.session_state.system_added = False

    # 초기 예산 계획 입력 폼
    if not st.session_state.initialized:
        with st.form("init_plan"):
            salary = st.number_input("월급 (만원)", min_value=0)
            goal_amount = st.number_input("목표 금액 (만원)", min_value=0)
            years = st.number_input("몇 년 안에 모으고 싶은가요?", min_value=1)
            submitted = st.form_submit_button("계획 요청")

        if submitted:
            # 영어 프롬프트 생성
            prompt = (
                f"My monthly salary is {salary}만원. I want to save {goal_amount}만원 in {years} years. "
                "Please create a detailed monthly budget plan in Korean. The plan must include the following categories: "
                "저축 (savings), 식비 (food), 주거비 (housing), 교통비 (transportation), 보험 (insurance), 쇼핑 (shopping). "
                "Make sure the plan is balanced and realistic to help achieve the savings goal. Respond in Korean."
            )

            # system 메시지 최초 1회만 추가
            if not st.session_state.system_added:
                system_message = {
                    "role": "system",
                    "content": (
                        "You are a financial assistant chatbot helping the user manage their monthly budget. "
                        "Always include and adjust these categories: 저축, 식비, 주거비, 교통비, 보험, 쇼핑. "
                        "Continue the conversation in Korean, updating the plan as the user requests."
                    )
                }
                st.session_state.messages.insert(0, system_message)
                st.session_state.system_added = True

            # 사용자 프롬프트 저장
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"월급: {salary}만원 / 목표: {goal_amount}만원 / 기간: {years}년")

            # GPT 응답 생성
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.initialized = True

    # 대화 유지 모드
    else:
        # 이전 대화 출력
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # 사용자 입력 받기
        if prompt := st.chat_input("예: 식비를 25만원으로 조정하고 싶어요"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # GPT 응답 생성 (system 메시지는 이미 포함되어 있음)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
            )

            with st.chat_message("assistant"):
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
