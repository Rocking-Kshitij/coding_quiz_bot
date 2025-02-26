import streamlit as st
import json

from langchain_core.prompts import PromptTemplate
import streamlit.components.v1 as components
from streamlit_ace import st_ace
from chat_bot_backend import log_conversation, init_db, get_question, store_result, get_correct_answer,get_feedback

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
for key in ['question', 'feedback', 'subtopic', 'difficulty', 'skill_name', 'lock_button', "code"]:
    if key not in st.session_state:
        st.session_state[key] = ""
# st.session_state['lock_button'] = False

# Function to get correct answer from LLM and store result
def get_correct_answer_and_store():
    correct_answer = get_correct_answer(st.session_state['question'])
    st.session_state['feedback'] = f"\n\n{correct_answer}"
    store_result(st.session_state['question'], "Unable to Solve", st.session_state['feedback'], st.session_state['difficulty'], st.session_state['skill_name'], st.session_state['subtopic'])
    

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Coding Practice Chatbot")
st.markdown("---")

left, right = st.columns([1.2, 1.8])

with left:
    # st.subheader("User Input & Code Editor")
    skill_name = st.selectbox("Select your skill", list(get_language_from_skill().keys()))
    st.session_state['skill_name'] = skill_name
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Get a Question"):
            question, subtopic, difficulty = get_question(skill_name)
            st.session_state.update({'question': question, 'subtopic': subtopic, 'difficulty': difficulty, 'feedback': "", 'lock_button':True})
            st.rerun()
    with col2:
        if st.button("Unable to Solve") and st.session_state['lock_button']:
            st.session_state['lock_button'] = False
            get_correct_answer_and_store()
            st.rerun()
    with col3:
        if st.button("Submit Answer")  and st.session_state['lock_button'] and len(st.session_state['code'])!=0:
            st.session_state['lock_button'] = False
            feedback = get_feedback(st.session_state['question'], st.session_state['code'])
            st.session_state['feedback'] = f"\n\n{feedback}"
            store_result(st.session_state['question'], st.session_state['code'], feedback, st.session_state['difficulty'], skill_name, st.session_state['subtopic'])
            st.rerun()

    # st.subheader("Question")
    st.write(f"{st.session_state['question']}")

with right:
    st.write("### Write Your Code Below:")
    code_editor = st_ace(language=get_language_from_skill().get(skill_name, "plaintext"), theme="monokai", key="code_editor", height=500)
    st.session_state['code'] = code_editor



# Full-width Feedback Section
st.markdown("---")
st.subheader("Feedback")
st.write(f"{st.session_state['feedback']}")

init_db()
