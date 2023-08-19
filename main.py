import openai
import streamlit as st
from utils.time_tracker import *
from prompt_templates.start_prompt import start_prompt
from prompt_templates.update_prompt import update_prompt
import asyncio
from datetime import datetime

# Interval in mintes, this needs to be set as an ENV var or via streamlit UI should be in hours
minutes = 30
interval_seconds = 60 * minutes


with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    telegram_token = st.text_input("Telegram Bot Token", key="telegram_bot_token", type="password")
    telegram_chat_id = st.text_input("Telegram Chat ID:", key="telegram_chat_id")
    unique_username = st.text_input("Username:", key="username")

if not all([openai_api_key]):
    st.info("Please provide all the required information in the sidebar to continue chatting.")
else:
    st.title("💬 Chatbot")
    if "messages" not in st.session_state:
        print(start_prompt())
        st.session_state["messages"] = [{"role": "system", "content": start_prompt()}]  # Starting with the start_prompt

    for msg in st.session_state.messages:
        if msg["role"] != "system":  # Skip system messages
            st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input():
        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)

# Function to run periodically, now includes sending the update_prompt
async def update_func():
    if "messages" in st.session_state:  # Check if messages exist
        update_messages = st.session_state.messages.copy()
        
        # Getting the current timestamp with full details
        timestamp = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S %p %Z") # Example: Sunday, August 19, 2023 17:30:15 PM UTC
        
        # Send the timestamp into update_prompt
        system_content = update_prompt(timestamp)
        update_messages.append({"role": "system", "content": system_content})
        
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=update_messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)
        
task = PeriodicTask(update_func, interval_seconds)
asyncio.run(task.start())