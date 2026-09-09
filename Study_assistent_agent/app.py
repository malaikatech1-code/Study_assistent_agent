import streamlit as st
from first_api_call import run_agent

st.title("📚 Study Assistant Agent")
st.write("Ask me to explain any topic — I remember your learning style over time.")

user_input = st.text_input("What do you want to learn about?")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        answer = run_agent(user_input)
    st.write(answer)