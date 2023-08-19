import openai
import streamlit as st
from utils.time_tracker import *
from prompt_templates.start_prompt import start_prompt
from prompt_templates.update_prompt import update_prompt
import asyncio
from datetime import datetime
from adapters.ingestion import ingest_document
import time
from datetime import datetime

def accumulate_non_system_messages(messages, last_ingested_index):
    return "\n".join(msg["content"] for index, msg in enumerate(messages) if msg["role"] != "system" and index > last_ingested_index)

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
        st.session_state["messages"] = [{"role": "system", "content": start_prompt()}]
    
    # Initialize a state to track the last ingested message index
    if "last_ingested_index" not in st.session_state:
        st.session_state["last_ingested_index"] = -1

    for msg in st.session_state.messages:
        if msg["role"] != "system":  # Skip system messages
            st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input():
        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        print(st.session_state.messages)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)

        non_system_messages = accumulate_non_system_messages(st.session_state.messages, st.session_state["last_ingested_index"])
        if non_system_messages: # Ingest only if there are new non-system messages
            ingest_document(non_system_messages)


def update_func():
    if "messages" in st.session_state:  # Check if messages exist
        update_messages = st.session_state.messages.copy()
        non_system_messages = accumulate_non_system_messages(update_messages, st.session_state["last_ingested_index"])
        if non_system_messages:  # Ingest only if there are new non-system messages
            ingest_document(non_system_messages)
            st.session_state["last_ingested_index"] = len(update_messages) - 1  # Update the last ingested index

        
        # Getting the current timestamp with full details
        timestamp = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S %p %Z") # Example: Sunday, August 19, 2023 17:30:15 PM UTC
        
        # Send the timestamp into update_prompt
        system_content = update_prompt(timestamp)
        update_messages.append({"role": "system", "content": system_content})
        
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=update_messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)
        
if 'last_run_time' not in st.session_state:
    st.session_state.last_run_time = 0

if time.time() - st.session_state.last_run_time > interval_seconds:
    update_func()
    st.session_state.last_run_time = time.time()