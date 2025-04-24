import streamlit as st
import json, atexit
from langchain_core.prompts import PromptTemplate
import streamlit.components.v1 as components
from streamlit_ace import st_ace
from chat_bot_backend import get_question, store_result,get_feedback, setup_database, get_question_data, get_rating
from chatbotconfig import get_connection

language_list = ["Python", "Bash", "FastAPI", "Streamlit", "Django"]
# Function to map skill name to programming language
def get_language_from_skill():
    # Subject : language
    return {
        "Any": "plain_text",
        "Python": "python",
        "Bash": "sh",
        "FastAPI": "python",
        # "Streamlit": "python",
        # "Django": "django",
        "SQL": "sql",
        # "PyTorch": "python",
        # "Kafka (Python)": "python",
        # "MongoDB": "sql",
        "Docker": "dockerfile",
        "Kubernetes": "yaml",
        "Terraform": "terraform",
        "JavaScript": "javascript",
        "React": "javascript",
        # "Ansible": "yaml",
        # "GitHub Actions": "yaml",
        # "Apache Airflow (Python)": "python",
        # "Git": "sh",
        "Pyspark": "python"

    }

# Initialize session state
for key in ['question', 'answer', 'question_data','skill_id', 'skill_name', 'feedback', 'question_id'\
     'subtopic', 'topic', 'unlock_button', "code", 'subject',\
         'language', 'score', 'conn', "question_level", "select_box", "locked_subject"]:
    if key not in st.session_state:
        if key == 'conn':
            st.session_state[key] = get_connection()
        elif key == 'unlock_button':
            st.session_state[key] = False
        elif key == 'select_box':
            st.session_state[key] = True
        elif key == 'subject':
            st.session_state[key] = "Any"
            st.session_state['language'] = get_language_from_skill().get(st.session_state['subject'])
        else:
            st.session_state[key] = ""

# st.session_state['subject'] = ""
# st.session_state['language'] = ""

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
    n_list = list(get_language_from_skill().keys())
    # st.session_state['unlock_button'] and 
    # if (not st.session_state['select_box']):
    #     st.session_state['select_box'] = True
    #     index = n_list.index(st.session_state['subject'])
    #     st.session_state['subject'] = st.selectbox(f"Current Subject here",n_list, index=index)
    #     st.rerun()
    if (st.session_state['select_box']):
        st.session_state['subject'] = st.selectbox(f"Current Subject here",n_list)
        st.session_state['language'] = get_language_from_skill().get(st.session_state['subject'])
    else:
        # index = n_list.index(st.session_state['subject'])
        st.session_state['subject'] = st.selectbox(f"Current Subject here",n_list, index=n_list.index(st.session_state['subject']))
        st.session_state['language'] = get_language_from_skill().get(st.session_state['subject'])
        
    with col1:
        if st.button("Get a Question"):
            with st.spinner("Fetching the question"):
                question, skill_id, subject, topic, subtopic, level, answer, q_id = get_question(st.session_state['conn'],st.session_state['subject'])
                language = get_language_from_skill().get(subject)
                # question_data = get_question_data(question, answer)
                question_data = ""
                st.session_state.update({'question': question, 'subtopic': subtopic, 'feedback': "", 'unlock_button':True,'select_box':False, 'skill_id':skill_id,\
                     'subject':subject, 'language':language, 'topic': topic, "question_level": level, "answer":answer, "question_data":question_data, "question_id":q_id, "locked_subject": subject})
                st.rerun()
    with col2:
        if st.button("Unable to Solve") and st.session_state['unlock_button']:
            with st.spinner("Fetching the feedback"):
                st.session_state.update({'feedback': f"\n\n{st.session_state['answer']}", 'score':0,'unlock_button':False, 'select_box':True,'subject': "Any"})
                store_result(st.session_state['conn'], st.session_state['question'], "Unable to Solve", st.session_state['answer'], st.session_state['score'], st.session_state['skill_id'], st.session_state['question_id'])
                st.rerun()
    with col3:
        if st.button("Submit Answer") and st.session_state['unlock_button'] and len(st.session_state['code'])!=0:
            with st.spinner("Fetching the feedback"):
                score = get_rating(st.session_state['question'], st.session_state['code'])
                feedback = st.session_state['answer']
                # st.session_state['feedback'] = f"\n\n{feedback}"
                # st.session_state['score'] = score
                store_result(st.session_state['conn'], st.session_state['question'], st.session_state['code'], st.session_state['answer'], score, st.session_state['skill_id'], st.session_state['question_id'])
                st.session_state.update({'feedback': f"\n\n{feedback}", 'score':score,'unlock_button':False,'select_box':True, 'subject': "Any"})
                st.rerun()

    # st.subheader("Question")# and st.session_state['subject'] != "Any"
    if st.session_state['question']!="":
        st.write(f"Subject: {st.session_state['locked_subject']}")
        st.write(f"Topic: {st.session_state['topic']} - Subtopic: {st.session_state['subtopic']}")
        st.write(f"Level: [{st.session_state['question_level']}]")
        st.write(f"{st.session_state['question']}")
        # st.expander("Get the Data").write(f"\n{st.session_state['question_data']}")

with right:
    st.write("### Write Your Code Below:")
    indx = list(set(get_language_from_skill().values())).index(st.session_state['language'])
    st.session_state['language'] = st.selectbox(f"Select coding language here",set(get_language_from_skill().values()), index = indx)
    st.write(f"Current language is {st.session_state['language']}")
    # code_editor = st_ace(language=get_language_from_skill().get(language, "plaintext"), theme="monokai", key="code_editor", height=500)
    code_editor = st_ace(language=st.session_state['language'],value="", theme="monokai", key="code_editor", height=500, auto_update=True,show_gutter=True, placeholder="Enter code here")
    st.session_state['code'] = code_editor



# Full-width Feedback Section
st.markdown("---")
if st.session_state['feedback'] !="":
    st.subheader("Feedback")
    st.write(f"Current score is: {st.session_state['score']}")
    st.write(f"{st.session_state['feedback']}")
    st.session_state['score'] = ""

# st.session_state['conn'].close()
# # setup_database(conn)
# if "conn" in st.session_state:
#     atexit.register(st.session_state['conn'].close())