import streamlit as st
from data import get_team_config, orchestrate
import asyncio
import os

def show_message(container, one_msg):
    with container:
        if one_msg.startswith("Developer"):
            with st.chat_message("ai"):
                st.markdown(one_msg)
        elif one_msg.startswith("CodeExecutor"):
            with st.chat_message("CodeExecutor"):
                st.markdown(one_msg)
        elif one_msg.startswith("Stopping reason"):
            with st.chat_message("user"):
                st.markdown(one_msg)

st.title("Talk with your dataset")

file = st.file_uploader("Upload your CSV file", type=["csv"])

if file is not None:
    # Save the uploaded file to a temporary location
    with open(os.path.join("temp", "data.csv"), "wb") as f:
        f.write(file.getbuffer())
    st.success("File uploaded successfully!")

prompt = st.chat_input(
    "Ask a question about your dataset, e.g., 'What are the columns in my dataset?'"
)

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

chat_container = st.container()

for one_msg in st.session_state['messages']:
    show_message(chat_container, one_msg)

if prompt:
    async def query():
        team, docker_agent = await get_team_config()
        # check if there's a saved state for the team, load it if exists
        if 'team_state' in st.session_state:
            await team.load_state(st.session_state['team_state'])

        with st.spinner("Generating response..."):
            async for one_msg in orchestrate(team, docker_agent, prompt):
                st.session_state.messages.append(one_msg)
                show_message(chat_container, one_msg)
                
                # get team's save state and store it in session state
                st.session_state['team_state'] = await team.save_state()
                
    asyncio.run(query())        