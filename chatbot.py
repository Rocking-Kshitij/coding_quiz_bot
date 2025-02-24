import streamlit as st
import sqlite3
import json
from lmstudio_llama import CustomLLamaLLM
from langchain_core.prompts import PromptTemplate
import streamlit.components.v1 as components
from streamlit_ace import st_ace

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
    c.execute("SELECT subtopic, AVG(CASE WHEN feedback LIKE '%incorrect%' THEN 1 ELSE 0 END) as error_rate FROM practice WHERE skill_name = ? GROUP BY subtopic ORDER BY error_rate DESC LIMIT 1", (skill_name,))
    result = c.fetchone()
    conn.close()
    
    if result:
        subtopic, _ = result
        difficulty = "Intermediate" if _ > 0.3 else "Advanced"
    else:
        subtopic, difficulty = "General", "Beginner"
    
    return subtopic, difficulty

# Function to get question from LLM based on past performance
def get_question(skill_name):
    subtopic, difficulty = determine_next_question(skill_name)
    idea_prompt = PromptTemplate(
        input_variable={"skill_name": "skill_name", "difficulty": "difficulty", "subtopic": "subtopic"},
        template="Generate a {difficulty} level coding question in {subtopic} for {skill_name}."
    )
    chain = idea_prompt | llm
    result = chain.invoke({"skill_name": skill_name, "difficulty": difficulty, "subtopic": subtopic})
    return result, subtopic, difficulty

# Function to get correct answer from LLM and store result
def get_correct_answer_and_store():
    correct_answer = get_correct_answer(st.session_state['question'])
    st.session_state['feedback'] = f"Correct Answer: {correct_answer}"
    store_result(st.session_state['question'], "Unable to Solve", st.session_state['feedback'], st.session_state['difficulty'], st.session_state['skill_name'], st.session_state['subtopic'])
    st.rerun()

# Function to get correct answer from LLM
def get_correct_answer(question):
    answer_prompt = PromptTemplate(
        input_variable={"question": "question"},
        template="Provide the correct answer for the following question:\n\n{question}\n\nAnswer:"
    )
    chain = answer_prompt | llm
    correct_answer = chain.invoke({"question": question})
    return correct_answer

# Function to evaluate the answer
def get_feedback(question, user_answer):
    feedback_prompt = PromptTemplate(
        input_variable={"question": "question", "user_answer": "user_answer"},
        template="Evaluate the following answer for the given question. Provide detailed feedback including correctness, improvements, and best practices.\n\nQuestion: {question}\nAnswer: {user_answer}\n\nFeedback:"
    )
    chain = feedback_prompt | llm
    feedback = chain.invoke({"question": question, "user_answer": user_answer})
    return feedback

# Function to store result in the database
def store_result(question, user_answer, feedback, difficulty, skill_name, subtopic):
    conn = sqlite3.connect("coding_practice.db")
    c = conn.cursor()
    c.execute("INSERT INTO practice (question, user_answer, feedback, difficulty, skill_name, subtopic) VALUES (?, ?, ?, ?, ?, ?)",
              (question, user_answer, feedback, difficulty, skill_name, subtopic))
    conn.commit()
    conn.close()

# Function to map skill name to programming language
def get_language_from_skill(skill_name):
    language_map = {
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
    return language_map.get(skill_name, "plaintext")

# Initialize session state
if 'question' not in st.session_state:
    st.session_state['question'] = ""
if 'feedback' not in st.session_state:
    st.session_state['feedback'] = ""
if 'subtopic' not in st.session_state:
    st.session_state['subtopic'] = ""
if 'difficulty' not in st.session_state:
    st.session_state['difficulty'] = ""
if 'skill_name' not in st.session_state:
    st.session_state['skill_name'] = ""

# Streamlit UI
st.set_page_config(layout="wide")  # Use full width
st.title("Coding Practice Chatbot")

st.markdown("---")

left, right = st.columns([1.2, 1.8])

with left:
    st.subheader("LLM Outputs")
    st.write(f"### Question: {st.session_state['question']}")
    st.write(f"### Feedback: {st.session_state['feedback']}")

with right:
    st.subheader("User Input & Code Editor")
    skill_name = st.selectbox("Select your skill", [
        "Python", "Bash", "FastAPI", "Streamlit", "Django", "SQL", "PyTorch", "Kafka (Python)", "MongoDB", "Docker", "Kubernetes", "Terraform", "Ansible", "GitHub Actions", "Apache Airflow (Python)", "Git", "Pyspark"
    ])
    st.session_state['skill_name'] = skill_name
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Get a Question"):
            question, subtopic, difficulty = get_question(skill_name)
            st.session_state['question'] = question
            st.session_state['subtopic'] = subtopic
            st.session_state['difficulty'] = difficulty
            st.session_state['feedback'] = ""
            st.rerun()
    with col2:
        if st.button("Unable to Solve"):
            get_correct_answer_and_store()
    
    st.write("### Write Your Code Below:")
    language = get_language_from_skill(skill_name)
    code_editor = st_ace(
        language=language, 
        theme="monokai", 
        key="code_editor",
        height=400
    )
    
    if st.button("Submit Answer"):
        feedback = get_feedback(st.session_state['question'], code_editor)
        st.session_state['feedback'] = feedback
        store_result(st.session_state['question'], code_editor, feedback, st.session_state['difficulty'], skill_name, st.session_state['subtopic'])
        st.rerun()

# Initialize database
init_db()
