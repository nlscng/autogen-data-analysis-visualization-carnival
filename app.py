import streamlit as st

st.title("Talk with your dataset")

prompt = st.chat_input(
    "Ask a question about your dataset, e.g., 'What are the columns in my dataset?'"
)

chat_container = st.container()

if prompt:
    with chat_container:
        st.write(f"You asked: {prompt}")
        # Here you would typically call the main function from data.py
        # and display the response. For now, we will just simulate a response.
        # response = "The columns in your dataset are: ['column1', 'column2', 'column3']"
        # st.write(f"Assistant: {response}")