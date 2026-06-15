import streamlit as st
import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from datetime import datetime
import json

GEMINI_API_KEY = "AIzaSyAHIqS2uzZbQkEr-ASA1YSJcunDuibHf14"
ARMORIQ_API_KEY = "ak_live_1ca54cbfe24aaf748af54e4bceb5602d73e8eb51c66c3f347195a1c04abdb86b"

genai.configure(api_key="GOOGLE_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.Client()

try:
    memory_db = client.get_collection("memory_twin")
except:
    memory_db = client.get_or_create_collection("memory_twin")


if "logs" not in st.session_state:
    st.session_state.logs = []


def armor_policy_check(query):
    blocked = [
        "password",
        "secret",
        "api key"
    ]

    for word in blocked:
        if word in query.lower():
            return False

    return True


def add_memory(text):

    vector = embedding_model.encode(text).tolist()

    memory_db.add(
        ids=[str(datetime.now())],
        documents=[text],
        embeddings=[vector]
    )


def retrieve_memory(query):

    vector = embedding_model.encode(query).tolist()

    result = memory_db.query(
        query_embeddings=[vector],
        n_results=3
    )

    return result["documents"][0]


def twin_response(query):

    if not armor_policy_check(query):
        return "Request blocked by ArmorIQ policy"

    memories = retrieve_memory(query)

    prompt = f"""
You are a personal digital memory twin.

Use these memories:
{memories}

Question:
{query}

Give advice based on the person's thinking style.
Do not claim to be the real person.
"""

    response = model.generate_content(prompt)

    answer = response.text

    st.session_state.logs.append(
        {
            "time":str(datetime.now()),
            "query":query,
            "response":answer
        }
    )

    return answer


st.set_page_config(
    page_title="Memory Twin AI",
    layout="wide"
)

st.title("🧠 Memory Twin AI")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Create Twin",
        "Chat With Twin",
        "Security Logs"
    ]
)


if menu=="Create Twin":

    st.header("Create Digital Memory Twin")

    name = st.text_input(
        "Person Name"
    )

    memory = st.text_area(
        "Enter memories, beliefs, experiences"
    )

    if st.button("Create Twin"):

        if memory:

            for item in memory.split("\n"):
                add_memory(item)

            st.success(
                f"{name}'s Memory Twin Created"
            )


elif menu=="Chat With Twin":

    st.header("Talk With Memory Twin")

    query = st.text_input(
        "Ask something"
    )

    if st.button("Ask"):

        if query:

            answer = twin_response(query)

            st.write(answer)


elif menu=="Security Logs":

    st.header("ArmorIQ Audit Logs")

    st.json(
        st.session_state.logs
    )
