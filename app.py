import streamlit as st

import os
import time
from openai import OpenAI

from carbolic import create_assistant, create_thread, send_message, generate_response

client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"})
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
OpenAI.api_key = os.environ["OPENAI_API_KEY"]

# - Params -------------------------------------------------------- #
assistant_name = "Carbolic"
assistant_instructions = "You are a legal assistant chatbot. Use your knowledge to perform tasks such as proofreading and answer retrieval to help your solicitor perform their tasks to the highest quality."
assistant_files = []
# ----------------------------------------------------------------- #

st.header("Carbolic", divider="rainbow")

if "model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-1106-preview"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "files_uploaded" not in st.session_state:
    st.session_state["files_uploaded"] = False

if "files" not in st.session_state:
    st.session_state["files"] = []

if "instructions" not in st.session_state:
    st.session_state["instructions"] = assistant_instructions

if "configurator_state" not in st.session_state:
    st.session_state["configurator_state"] = True


def toggle_closed():
    st.session_state["configurator_state"] = False


with st.expander("Configurator", expanded=st.session_state["configurator_state"]):
    st.session_state["instructions"] = st.text_area(
        label="Instructions", value=st.session_state["instructions"]
    )

    assistant_files = st.file_uploader("Files", accept_multiple_files=True)

    if assistant_files:
        st.session_state["files"] = assistant_files

    if not st.session_state["files_uploaded"] and assistant_files:
        if st.button("Confirm Files", on_click=toggle_closed):
            st.session_state["files_uploaded"] = True
            st.success("File Upload Success!")

    if not st.session_state["files_uploaded"]:
        if st.button("Skip Upload", on_click=toggle_closed):
            st.session_state["files_uploaded"] = True
            st.success("File Upload Skipped")


if st.session_state["files_uploaded"]:
    assistant = create_assistant(
        client,
        name=assistant_name,
        instructions=st.session_state["instructions"],
        files=st.session_state["files"],
    )

    thread = create_thread(client)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Hey Carbolic, ..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        message, log = send_message(client, thread, prompt)
        st.session_state.messages.append(log)

        with st.chat_message("assistant"):
            run, log = generate_response(client, thread, assistant)
            st.markdown(log["content"])

        st.session_state.messages.append(log)
else:
    st.info("Please upload files or skip upload to proceed.")

footer="""<style>
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
font-size: 6;
background-color: transparent;
color: auto;
text-align: center;
}
</style>
<div class="footer">
<p>Made by Kai</p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
