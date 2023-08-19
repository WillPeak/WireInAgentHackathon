import openai
import streamlit as st
from utils.time_tracker import *

# Interval in seconds this needs to be set as an ENV var or via streamlit ui should be in hours
interval_seconds = 30

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    telegram_token = st.text_input("Telegram Bot Token", key="telegram_bot_token", type="password")
    telegram_chat_id = st.text_input("Telegram Chat ID:", key="telegram_chat_id")

st.title("💬 Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    openai.api_key = openai_api_key
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.chat_message("assistant").write(msg.content)

# Example function to run periodically
async def my_function():
    print("Function executed!")

task = PeriodicTask(my_function, interval_seconds)
asyncio.run(task.start())