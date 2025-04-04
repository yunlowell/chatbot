import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import re

# 제목 및 설명
st.title("💬 yun's 월급 관리 Chatbot")
st.write(
    "이 챗봇은 월급과 목표 금액, 기간을 기반으로 예산 계획을 세우고 "
    "저축, 식비, 주거비, 교통비, 보험, 쇼핑 항목을 포함해 지출 조정을 도와줍니다.\n"
    "또한 저축률, 총 예상 저축액, 월별 저축 그래프도 확인할 수 있어요."
)

# API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("계속하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    if not st.session_state.initialized:
        with st.form("init_plan"):
            salary = st.number_input("월급 (만원)", min_value=0)
            goal_amount = st.number_input("목표 금액 (만원)", min_value=0)
            years = st.number_input("몇 년 안에 모으고 싶은가요?", min_value=1)
            submitted = st.form_submit_button("계획 요청")

        if submitted:
            prompt = (
                f"My monthly salary is {salary}만원. I want to save {goal_amount}만원 in {years} years. "
                "Please create a detailed monthly budget plan in Korean. The plan must include the following categories: "
                "저축 (savings), 식비 (food), 주거비 (housing), 교통비 (transportation), 보험 (insurance), 쇼핑 (shopping). "
                "Make sure the plan is balanced and realistic to help achieve the savings goal. Respond in Korean."
            )

            st.session_state.salary = salary
            st.session_state.goal_amount = goal_amount
            st.session_state.years = years
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(f"월급: {salary}만원 / 목표: {goal_amount}만원 / 기간: {years}년")

            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
            )
            with st.chat_message("assistant"):
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.initialized = True

    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("예: 식비를 25만원으로 바꿔줘"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            system_message = {
                "role": "system",
                "content": (
                    "You are a financial assistant chatbot helping the user manage their monthly budget. "
                    "Always include and adjust these categories: 저축, 식비, 주거비, 교통비, 보험, 쇼핑. "
                    "Continue the conversation in Korean, updating the plan as the user requests."
                )
            }

            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[system_message] + st.session_state.messages,
                stream=True,
            )
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # === 계산 및 시각화 ===
        last_response = ""
        for m in reversed(st.session_state.messages):
            if m["role"] == "assistant":
                last_response = m["content"]
                break

        # 예산 항목 추출
        pattern = r"(저축|식비|주거비|교통비|보험|쇼핑)\s*[:\-]?\s*([0-9]+)\s*만원"
        matches = re.findall(pattern, last_response)
        if matches:
            category_labels = []
            category_values = []
            for category, value in matches:
                category_labels.append(category)
                category_values.append(int(value))

            total_spending = sum(category_values)
            salary = st.session_state.salary
            years = st.session_state.years
            savings = next((v for c, v in zip(category_labels, category_values) if c == "저축"), 0)

            st.subheader("📊 예산 요약")
            st.markdown(f"**저축률**: {round((savings / salary) * 100, 2)}%")
            st.markdown(f"**총 예상 저축액 (약)**: {savings * 12 * years:,}만원")

            # 그래프
            fig, ax = plt.subplots()
            months = [f"{i+1}월" for i in range(12)]
            monthly_savings = [savings] * 12
            ax.plot(months, monthly_savings, marker='o')
            ax.set_title("월별 저축 예상액")
            ax.set_ylabel("저축액 (만원)")
            st.pyplot(fig)
