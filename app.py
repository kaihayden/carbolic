
import streamlit as st

import os
import time
from openai import OpenAI

from carbolic import create_assistant, create_thread, send_message, generate_response

client = OpenAI()
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
OpenAI.api_key = os.environ["OPENAI_API_KEY"]

# - Params -------------------------------------------------------- #
assistant_name = 'Carbolic'
assistant_instructions = """
You are a legal assistant chatbot. Use your knowledge to perform tasks such as proofreading and answer retrieval to help your solicitor perform their tasks to the highest quality.
"""
assistant_files=[]
# ----------------------------------------------------------------- #

st.title("Carbolic by Kai")

if "model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-1106-preview"

if "messages" not in st.session_state:
    st.session_state.messages = []

assistant_files = st.file_uploader("Select Files", accept_multiple_files=True)
assistant = create_assistant(client, name=assistant_name, instructions=assistant_instructions, files=assistant_files)

thread = create_thread(client)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Hey Carbolic, ..."):

    message, log = send_message(client, thread, prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(log)

    with st.chat_message("assistant"):

        run, log = generate_response(client, thread, assistant)

        message_placeholder = st.empty()
        message_placeholder.markdown(log['content'])

    st.session_state.messages.append(log)