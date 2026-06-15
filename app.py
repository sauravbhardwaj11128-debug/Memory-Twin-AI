import streamlit as st
import google.generativeai as genai
import chromadb

st.set_page_config(page_title="Memory Twin AI")

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

client = chromadb.Client()
memory_db = client.get_or_create_collection("memory_twin")

st.title("Memory Twin AI")

if "history" not in st.session_state:
    st.session_state.history = []

name = st.text_input("Name")
experience = st.text_area("Experience")
habits = st.text_area("Habits")

if st.button("Save Memory"):
    text = f"Name: {name}\nExperience: {experience}\nHabits: {habits}"
    memory_db.upsert(
        ids=["user_memory"],
        documents=[text]
    )
    st.success("Memory saved")

query = st.text_input("Ask your twin")

if query:
    data = memory_db.get(ids=["user_memory"])

    context = ""
    if data["documents"]:
        context = data["documents"][0]

    prompt = f"""
You are a digital twin of a person.
Answer according to their stored information.

User profile:
{context}

Question:
{query}
"""

    response = model.generate_content(prompt)

    st.write(response.text)
