import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# API 키 불러오기
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    if not GOOGLE_API_KEY:
        st.error("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 GOOGLE_API_KEY를 설정해주세요.")
        st.stop()
except Exception as e:
    st.error("API 키를 불러오는 중 오류가 발생했습니다. .streamlit/secrets.toml 파일이 올바르게 설정되어 있는지 확인해주세요.")
    st.stop()

# Gemini 모델 초기화
try:
    genai.configure(api_key=GOOGLE_API_KEY)

    for m in genai.list_models():
        print(m.name, m.supported_generation_methods)

    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Gemini 모델 초기화 중 오류가 발생했습니다. API 키가 올바른지 확인해주세요.")
    st.stop()

# 세션 상태 초기화
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Set page config
st.set_page_config(
    page_title="승우네 챗봇",
    page_icon="🤖",
    layout="centered"
)

# Add custom CSS
st.markdown("""
<style>
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("승우네 챗봇")
st.markdown("승우네 API를 활용한 기본 챗봇 프레임워크입니다.")

# 이전 대화 내용 표시
with st.expander("이전 대화 보기", expanded=False):
    if not st.session_state.chat_history:
        st.info("아직 대화 내용이 없습니다.")
    else:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"**사용자 {i//2 + 1}**: {message['content']}")
            else:
                st.markdown(f"**Gemini {i//2 + 1}**: {message['content']}")
            st.divider()

# Display chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("메시지를 입력하세요...")

# 입력된 메시지가 있을 경우 처리
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
    
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response.text}) 
