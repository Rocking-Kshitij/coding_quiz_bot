import streamlit as st
import json
from langchain_core.prompts import PromptTemplate
import streamlit.components.v1 as components
from streamlit_ace import st_ace
from chat_bot_backend import get_question, store_result, get_correct_answer,get_feedback, conn, setup_database

language_list = ["Python", "Bash", "FastAPI", "Streamlit", "Django"]
# Function to map skill name to programming language
def get_language_from_skill():
    # Subject : language
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
        "Terraform": "plain_text",
        "Ansible": "yaml",
        "GitHub Actions": "yaml",
        "Apache Airflow (Python)": "python",
        "Git": "bash",
        "Pyspark": "python"
    }

# Initialize session state
for key in ['question', 'skill_id', 'skill_name', 'feedback', 'subtopic', 'topic', 'lock_button', "code", 'subject', 'language', 'score']:
    if key not in st.session_state:
        st.session_state[key] = ""
# st.session_state['lock_button'] = False
st.session_state['subject'] = ""
st.session_state['language'] = ""

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Coding Practice Chatbot")
st.markdown("---")
left, right = st.columns([1.2, 1.8])

with left:
    # st.subheader("User Input & Code Editor")
    # skill_name = st.selectbox("Select your skill", list(get_language_from_skill().keys()))
    # st.session_state['skill_name'] = skill_name
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # st.session_state['subject']  = st.selectbox(f"Current language is {st.session_state['language']}",["Any"]+list(get_language_from_skill().keys()))
    st.session_state['subject']  = st.selectbox(f"Current Subject here",["Any"]+list(get_language_from_skill().keys()))
    st.session_state['language'] = get_language_from_skill().get(st.session_state['subject'])
    with col1:
        if st.button("Get a Question"):
            question, skill_id, subject, topic, subtopic = get_question(conn,st.session_state['subject'])
            language = get_language_from_skill().get(subject)
            st.session_state.update({'question': question, 'subtopic': subtopic, 'feedback': "", 'lock_button':True, 'skill_id':skill_id, 'subject':subject, 'language':language, 'topic': topic})
            st.rerun()
    with col2:
        if st.button("Unable to Solve") and st.session_state['lock_button']:
            st.session_state['lock_button'] = False
            correct_answer = get_correct_answer(st.session_state['question'])
            st.session_state['feedback'] = f"\n\n{correct_answer}"
            st.session_state['score'] = 0
            store_result(conn, st.session_state['question'], "Unable to Solve", correct_answer, st.session_state['score'], st.session_state['skill_id'])
            st.rerun()
    with col3:
        if st.button("Submit Answer")  and st.session_state['lock_button'] and len(st.session_state['code'])!=0:
            st.session_state['lock_button'] = False
            feedback, score = get_feedback(st.session_state['question'], st.session_state['code'])
            st.session_state['feedback'] = f"\n\n{feedback}"
            st.session_state['score'] = score
            store_result(conn, st.session_state['question'], st.session_state['code'], feedback, score, st.session_state['skill_id'])
            st.rerun()

    # st.subheader("Question")
    st.write(f"{st.session_state['question']}")

with right:
    st.write("### Write Your Code Below:")
    if (st.session_state['subject'] == "Any"):
        indx = 1
    else:
        indx = list(set(get_language_from_skill().values())).index(st.session_state['language'])
    st.session_state['language'] = st.selectbox(f"Select coding language here",set(get_language_from_skill().values()), index = indx)
    st.write(f"Current language is {st.session_state['language']}")
    # code_editor = st_ace(language=get_language_from_skill().get(language, "plaintext"), theme="monokai", key="code_editor", height=500)
    code_editor = st_ace(language=st.session_state['language'],value="", theme="monokai", key="code_editor", height=500, auto_update=True,show_gutter=True)
    st.session_state['code'] = code_editor



# Full-width Feedback Section
st.markdown("---")
if st.session_state['lock_button'] == False:
    st.subheader("Feedback")
    st.write(f"Current score is: {st.session_state['score']}")
    st.write(f"{st.session_state['feedback']}")
    st.session_state['score'] = ""


# setup_database(conn)