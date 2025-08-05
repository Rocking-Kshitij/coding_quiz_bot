import streamlit as st
import psycopg2
import numpy as np
from lmstudio_llama import CustomLLamaLLM, CustomEmbedding
from langchain_core.prompts import PromptTemplate

# Load Embedding & LLM Model
embeddings = CustomEmbedding("text-embedding-nomic-embed-text-v1.5@q8_0")
llama_model = "llama-3.2-3b-instruct"
llm = CustomLLamaLLM(llama_model=llama_model)

# LLM Prompt
idea_prompt = PromptTemplate(
    input_variable={"skill_name": "skill_name", "skill_level": "skill_level"},
    template="Generate a coding question for someone with {skill_level} expertise in {skill_name}."
)

# Database connection
conn = psycopg2.connect(
    dbname="ai_test_db",
    user="data_pgvector_user",
    password="data_pgvector_password",
    host="localhost",
    port="5435"
)
cursor = conn.cursor()

# --------- FUNCTION DEFINITIONS ---------
def fetch_user_skills(user_id):
    cursor.execute("SELECT skill_name FROM user_skills WHERE user_id = %s", (user_id,))
    return [row[0] for row in cursor.fetchall()]

def find_weak_concepts(user_id):
    cursor.execute(
        """
        SELECT concept FROM user_weak_areas 
        WHERE user_id = %s 
        ORDER BY avg_rating ASC, attempts DESC LIMIT 3
        """,
        (user_id,)
    )
    return [row[0] for row in cursor.fetchall()]

def store_quiz_history(user_id, question, answer, feedback, rating, difficulty, concepts):
    cursor.execute(
        "INSERT INTO quiz_history (user_id, question, answer, llm_feedback, rating, difficulty, concepts) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (user_id, question, answer, feedback, rating, difficulty, concepts)
    )
    conn.commit()

    # Update Weak Areas
    for concept in concepts:
        cursor.execute(
            """
            INSERT INTO user_weak_areas (user_id, concept, avg_rating, attempts)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (user_id, concept) 
            DO UPDATE SET 
                avg_rating = (user_weak_areas.avg_rating * user_weak_areas.attempts + %s) / (user_weak_areas.attempts + 1),
                attempts = user_weak_areas.attempts + 1
            """,
            (user_id, concept, rating, rating)
        )
    conn.commit()

def find_similar_questions(last_question):
    embedding = embeddings.embed_query(last_question)
    embedding_array = np.array(embedding).tolist()

    cursor.execute(
        "SELECT question FROM question_embeddings ORDER BY embedding <-> %s::vector LIMIT 3",
        (embedding_array,)
    )
    return [row[0] for row in cursor.fetchall()]

def generate_next_question(user_id):
    weak_concepts = find_weak_concepts(user_id)
    if weak_concepts:
        top_concept = weak_concepts[0]
        chain = idea_prompt | llm
        return chain.invoke({"skill_name": top_concept, "skill_level": "intermediate"})
    return "No weak areas detected. Ask a general question."

# --------- STREAMLIT UI ---------
st.title("🎯 AI Code Quiz")

# User Authentication (Simple)
user_id = st.text_input("Enter your User ID", value="1")

if user_id:
    user_id = int(user_id)

    # Show User's Skills
    skills = fetch_user_skills(user_id)
    st.sidebar.header("🛠️ Your Skills")
    for skill in skills:
        st.sidebar.write(f"✅ {skill}")

    # Show Weak Areas
    weak_concepts = find_weak_concepts(user_id)
    st.sidebar.header("⚠️ Weak Concepts")
    if weak_concepts:
        for concept in weak_concepts:
            st.sidebar.write(f"❌ {concept}")
    else:
        st.sidebar.write("No weak areas detected!")

    # Generate a Question
    if "current_question" not in st.session_state:
        st.session_state.current_question = generate_next_question(user_id)

    st.subheader("📌 Your Question")
    st.write(st.session_state.current_question)

    # User Input for Answer
    user_answer = st.text_area("✍️ Your Answer")

    if st.button("Submit Answer"):
        if user_answer:
            # Simulated Feedback & Rating
            feedback = f"Good attempt, but you can improve!"
            rating = np.random.uniform(4, 9)  # Randomized for now
            difficulty = "medium"
            concepts = ["Python", "OOP"]  # Placeholder concepts for now

            st.success("✅ Answer Submitted!")
            st.subheader("📢 LLM Feedback")
            st.write(feedback)
            st.subheader(f"⭐ Rating: {round(rating, 1)}/10")

            # Store result
            store_quiz_history(user_id, st.session_state.current_question, user_answer, feedback, rating, difficulty, concepts)

            # Fetch Similar Questions
            similar_qs = find_similar_questions(st.session_state.current_question)
            st.subheader("🔍 Related Questions")
            for q in similar_qs:
                st.write(f"🔹 {q}")

            # Generate New Question
            st.session_state.current_question = generate_next_question(user_id)

            st.button("Next Question", type="primary")
        else:
            st.warning("⚠️ Please enter an answer before submitting!")

