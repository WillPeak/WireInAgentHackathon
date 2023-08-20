import openai
import streamlit as st
from utils.time_tracker import *
from prompt_templates.start_prompt import start_prompt
from prompt_templates.update_prompt import update_prompt
from datetime import datetime
from adapters.ingestion import ingest_user_chat
from datetime import datetime
import time
import threading
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx



wait_time = 15 #seconds



def accumulate_and_ingest_non_system_messages(messages, last_ingested_index, username):
    non_system_messages = "\n".join(msg["content"] for index, msg in enumerate(messages) if msg["role"] != "system" and index > last_ingested_index)
    if non_system_messages:
        ingest_user_chat(username, non_system_messages, datetime.now().isoformat())  # Assuming username and timestamp are parameters
    return non_system_messages

last_update_time = datetime.now()
def update_func():
    print()
    if "messages" in st.session_state:  # Check if messages exist
        update_messages = st.session_state.messages.copy()
        accumulate_and_ingest_non_system_messages(st.session_state.messages, st.session_state["last_ingested_index"], unique_username)  # unique_username assumed to be user's username
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
        t = threading.Thread(target=delay_notify)
        add_script_run_ctx(t)
        t.start()


def delay_notify():
    time.sleep(5)
    update_func()


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
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)

        accumulate_and_ingest_non_system_messages(st.session_state.messages, st.session_state["last_ingested_index"], unique_username)  # unique_username assumed to be user's username


        t = threading.Thread(target=delay_notify)
        add_script_run_ctx(t)
        t.start()