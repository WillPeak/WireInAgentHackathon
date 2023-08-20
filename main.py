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

load_dotenv()



wait_time = int(os.getenv('INTERVAL_TIME_MINUTES')) * 60 #seconds
unique_username = os.getenv('USERNAME')
openai_api_key = os.getenv('OPENAI_API_KEY')
active_threads = []
MODEL = os.getenv('MODEL')


def accumulate_and_ingest_messages(messages, last_ingested_index, username):
    print(last_ingested_index)
    messages = [msg for index, msg in enumerate(messages) if index > last_ingested_index]
    if messages:
        ingest_user_chat(username, messages, datetime.now().isoformat())  # Assuming username and timestamp are parameters
    return messages

last_update_time = datetime.now()
def update_func():
    # Clear the list of active threads
    active_threads.clear()
    if "messages" in st.session_state:  # Check if messages exist
        update_messages = st.session_state.messages.copy()
        accumulate_and_ingest_messages(st.session_state.messages, st.session_state["last_ingested_index"], unique_username)  # unique_username assumed to be user's username
        st.session_state["last_ingested_index"] = len(update_messages) - 1  # Update the last ingested index

        # Getting the current timestamp with full details
        timestamp = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S %p %Z") # Example: Sunday, August 19, 2023 17:30:15 PM UTC
        
        # Send the timestamp into update_prompt
        system_content = update_prompt(timestamp)
        update_messages.append({"role": "user", "content": system_content})
        
        response = openai.ChatCompletion.create(model=MODEL, messages=update_messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)       
        t = threading.Thread(target=delay_notify)
        add_script_run_ctx(t)
        active_threads.append(t) # Add the new thread to the list
        t.start()


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
        st.session_state["last_ingested_index"] = -1

    for index, msg in enumerate(st.session_state.messages):
        if msg["role"] != "system" and index > 1:  # Skip system messages
            st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input():
        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = openai.ChatCompletion.create(model=MODEL, messages=st.session_state.messages)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)

        accumulate_and_ingest_messages(st.session_state.messages, st.session_state["last_ingested_index"], unique_username)  # unique_username assumed to be user's username
        t = threading.Thread(target=delay_notify)
        add_script_run_ctx(t)
        active_threads.append(t) # Add the new thread to the list
        t.start()