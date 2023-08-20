import openai
import streamlit as st
from utils.time_tracker import *
from prompt_templates.start_prompt import start_prompt, system_prompt
from prompt_templates.update_prompt import update_prompt
from datetime import datetime
from adapters.ingestion import ingest_user_chat
from datetime import datetime
import time
import os
import threading
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv()


wait_time = int(os.getenv('INTERVAL_TIME_MINUTES')) * 60 #seconds
unique_username = os.getenv('USERNAME')
openai_api_key = os.getenv('OPENAI_API_KEY')
active_threads = []
MODEL = os.getenv('MODEL')
st_autorefresh(interval=10000, key="chatupdate")

def check_time_passed():
    if 'last_time_user_input' in st.session_state:
        time_now = datetime.now()
        time_elapsed = (time_now - st.session_state['last_time_user_input']).total_seconds() / 60

        if time_elapsed >= wait_time/60:
            return True
        return False

def accumulate_and_ingest_messages(messages, username):

    messages = [msg for index, msg in enumerate(messages) if index > st.session_state["last_ingested_index"] - 1 and index != 1 and index != 2]
    if messages:
        ingest_user_chat(username, messages, datetime.now().isoformat())  # Assuming username and timestamp are parameters
        st.session_state["last_ingested_index"] = len(st.session_state.messages)
    return messages

def update_func():
    if not check_time_passed():
        return
    # Clear the list of active threads
    active_threads.clear()
    if "messages" in st.session_state:  # Check if messages exist
        update_messages = st.session_state.messages.copy()

        # Getting the current timestamp with full details
        timestamp = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S %p %Z")  # Example: Sunday, August 19, 2023 17:30:15 PM UTC

        # Send the timestamp into update_prompt
        content = update_prompt(timestamp)
        update_messages.append({"role": "user", "content": content})

        response = openai.ChatCompletion.create(model=MODEL, messages=update_messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        

        st.chat_message("assistant").write(msg.content)
        
        print(msg.content)
        accumulate_and_ingest_messages(st.session_state.messages, unique_username)  # unique_username assumed to be user's username
        

def delay_notify():
    time.sleep(wait_time)
    update_func()


with st.sidebar:
    telegram_token = st.text_input("Telegram Bot Token", key="telegram_bot_token", type="password")
    telegram_chat_id = st.text_input("Telegram Chat ID:", key="telegram_chat_id")

if not all([openai_api_key, unique_username]):
    st.info("Please provide and openai key, and username in your .env file.")
else:
    st.title("💬 Chatbot")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": system_prompt() }]
        st.session_state["messages"].append({"role": "user", "content": start_prompt() })
        st.session_state["messages"].append({"role": "assistant", "content": "Hi I am intention bot. I am here to ask you questions about your intentions" })

    
    # Initialize a state to track the last ingested message index
    if "last_ingested_index" not in st.session_state:
        st.session_state["last_ingested_index"] = 2

    for index, msg in enumerate(st.session_state.messages):
        if msg["role"] != "system" and index > 1:  # Skip system messages
            st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input():
        active_threads.clear()
        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = openai.ChatCompletion.create(model=MODEL, messages=st.session_state.messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)
        accumulate_and_ingest_messages(st.session_state.messages, unique_username)  # unique_username assumed to be user's username
        st.session_state['last_time_user_input'] = datetime.now()
        t = threading.Thread(target=delay_notify)
        add_script_run_ctx(t)
        active_threads.append(t) # Add the new thread to the list
        t.start()
