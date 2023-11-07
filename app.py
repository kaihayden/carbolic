
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

if 'files_uploaded' not in st.session_state:
    st.session_state['files_uploaded'] = False

if 'files' not in st.session_state:
    st.session_state['files'] = []

# File uploader
assistant_files = st.file_uploader("Select Files", accept_multiple_files=True)

# If files are uploaded, update the session state
if assistant_files:
    st.session_state['files'] = assistant_files

# Confirm button - only show if files are uploaded or not confirmed yet
if not st.session_state['files_uploaded'] and uploaded_files:
    if st.button('Confirm Files'):
        st.session_state['files_uploaded'] = True

# Skip upload button - only show if not confirmed yet
if not st.session_state['files_uploaded']:
    if st.button('Skip Upload'):
        st.session_state['files_uploaded'] = True

# Logic to hide or show the uploader based on the session state
if st.session_state['files_uploaded']:
    st.success('Files are confirmed!')
    
    assistant = create_assistant(client, name=assistant_name, instructions=assistant_instructions, files=st.session_state['files'])

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
else:
    st.info('Please upload files or skip upload to proceed.')

