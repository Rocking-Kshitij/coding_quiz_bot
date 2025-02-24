import streamlit as st
import sqlite3
import json
import logging
from datetime import datetime
from lmstudio_llama import CustomLLamaLLM
from langchain_core.prompts import PromptTemplate
import streamlit.components.v1 as components
from streamlit_ace import st_ace
import numpy as np

# Configure logging to write logs to a file
logging.basicConfig(
    filename="llm_conversation.log",
    level=logging.INFO,
    format="%(asctime)s - User: %(message)s\n%(asctime)s - LLM: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_conversation(user_prompt, llm_response):
    """Logs the conversation between user and LLM in the correct format."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("llm_conversation.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"\n{timestamp}\nUser: {user_prompt}\nLLM: {llm_response}\n")

# Initialize custom LLM
llama_model3b = "llama-3.2-3b-instruct"
llm = CustomLLamaLLM(llama_model=llama_model3b)

# Database setup
def init_db():
    conn = sqlite3.connect("coding_practice.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS practice (
                    id INTEGER PRIMARY KEY,
                    question TEXT,
                    user_answer TEXT,
                    feedback TEXT,
                    difficulty TEXT,
                    skill_name TEXT,
                    subtopic TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

# Function to analyze past performance and determine the next question
def determine_next_question(skill_name):
    conn = sqlite3.connect("coding_practice.db")
    c = conn.cursor()
    c.execute("""
        SELECT subtopic, difficulty, 
               CASE 
                   WHEN feedback LIKE '%incorrect%' THEN 1 
                   ELSE 0 
               END as error_flag,
               timestamp
        FROM practice 
        WHERE skill_name = ? 
        ORDER BY timestamp DESC
        LIMIT 10
    """, (skill_name,))
    
    data = c.fetchall()
    conn.close()
    
    if not data:
        return "General", "Beginner"
    
    subtopic_performance = {}
    difficulty_levels = ["Beginner", "Easy Intermediate", "Hard Intermediate", "Advanced"]
    
    for subtopic, difficulty, error, timestamp in data:
        if subtopic not in subtopic_performance:
            subtopic_performance[subtopic] = []
        subtopic_performance[subtopic].append(error)
    
    weakest_subtopic = max(subtopic_performance, key=lambda sub: np.mean(subtopic_performance[sub]))
    avg_error_rate = np.mean(subtopic_performance[weakest_subtopic])
    
    if avg_error_rate > 0.6:
        next_difficulty = "Beginner"
    elif avg_error_rate > 0.4:
        next_difficulty = "Easy Intermediate"
    elif avg_error_rate > 0.2:
        next_difficulty = "Hard Intermediate"
    else:
        next_difficulty = "Advanced"
    
    return weakest_subtopic, next_difficulty

# Function to get question from LLM based on past performance
def get_question(skill_name):
    subtopic, difficulty = determine_next_question(skill_name)
    idea_prompt = f"Generate a {difficulty} level coding question in {subtopic} for {skill_name}."
    response = llm.invoke(idea_prompt)
    log_conversation(idea_prompt, response)
    return response, subtopic, difficulty

# Function to get correct answer from LLM and store result
def get_correct_answer_and_store():
    correct_answer = get_correct_answer(st.session_state['question'])
    st.session_state['feedback'] = f"Correct Answer: {correct_answer}"
    store_result(st.session_state['question'], "Unable to Solve", st.session_state['feedback'], st.session_state['difficulty'], st.session_state['skill_name'], st.session_state['subtopic'])
    st.rerun()

# Function to get correct answer from LLM
def get_correct_answer(question):
    answer_prompt = f"Provide the correct answer for the following question:\n\n{question}\n\nAnswer:"
    response = llm.invoke(answer_prompt)
    log_conversation(answer_prompt, response)
    return response

# Function to evaluate the answer
def get_feedback(question, user_answer):
    feedback_prompt = f"Evaluate the following answer for the given question. Provide detailed feedback including correctness, improvements, and best practices.\n\nQuestion: {question}\nAnswer: {user_answer}\n\nFeedback:"
    response = llm.invoke(feedback_prompt)
    log_conversation(feedback_prompt, response)
    return response

# Function to store result in the database
def store_result(question, user_answer, feedback, difficulty, skill_name, subtopic):
    conn = sqlite3.connect("coding_practice.db")
    c = conn.cursor()
    c.execute("INSERT INTO practice (question, user_answer, feedback, difficulty, skill_name, subtopic) VALUES (?, ?, ?, ?, ?, ?)",
              (question, user_answer, feedback, difficulty, skill_name, subtopic))
    conn.commit()
    conn.close()

# Function to map skill name to programming language
def get_language_from_skill():
    return {
        "Python": "python",
        "Bash": "bash",
        "FastAPI": "python",
        "Streamlit": "python",
        "Django": "python",
        "SQL": "sql",
        "PyTorch": "python",
        "Kafka (Python)": "python",
        "MongoDB": "sql",
        "Docker": "bash",
        "Kubernetes": "yaml",
        "Terraform": "hcl",
        "Ansible": "yaml",
        "GitHub Actions": "yaml",
        "Apache Airflow (Python)": "python",
        "Git": "bash",
        "Pyspark": "python"
    }

# Initialize session state
for key in ['question', 'feedback', 'subtopic', 'difficulty', 'skill_name']:
    if key not in st.session_state:
        st.session_state[key] = ""

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Coding Practice Chatbot")
st.markdown("---")
left, right = st.columns([1.2, 1.8])
with left:
    st.subheader("LLM Outputs")
    st.write(f"### Question: {st.session_state['question']}")
    st.write(f"### Feedback: {st.session_state['feedback']}")
with right:
    st.subheader("User Input & Code Editor")
    skill_name = st.selectbox("Select your skill", list(get_language_from_skill().keys()))
    st.session_state['skill_name'] = skill_name
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Get a Question"):
            question, subtopic, difficulty = get_question(skill_name)
            st.session_state.update({'question': question, 'subtopic': subtopic, 'difficulty': difficulty, 'feedback': ""})
            st.rerun()
    with col2:
        if st.button("Unable to Solve"):
            get_correct_answer_and_store()
    st.write("### Write Your Code Below:")
    code_editor = st_ace(language=get_language_from_skill().get(skill_name, "plaintext"), theme="monokai", key="code_editor", height=400)
    if st.button("Submit Answer"):
        feedback = get_feedback(st.session_state['question'], code_editor)
        st.session_state['feedback'] = feedback
        store_result(st.session_state['question'], code_editor, feedback, st.session_state['difficulty'], skill_name, st.session_state['subtopic'])
        st.rerun()
init_db()
