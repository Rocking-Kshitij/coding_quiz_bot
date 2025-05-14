from chatbotconfig import get_connection, embeddings
from chat_bot_backend import get_question, get_dict_result, get_next_skill
import time, json
from datetime import datetime
from chatbotconfig import llm
from langchain_core.prompts import PromptTemplate


conn = get_connection()
# # # verify_question_created(conn)
# # subject = "FastAPI"
# # question, skill_id, subject, topic, subtopic, level, answer = get_question(conn, subject)
# # for item in [question, skill_id, subject, topic, subtopic, level, answer]:
# #     print(item)
# #     print("---------------------------------------")
# #     time.sleep(10)
# cursor = conn.cursor()

# cursor.execute(
#     """
#     SELECT skillid, subject, topic, subtopic
#     FROM Skills
#     WHERE content IS NULL
#     """
# )

# skills = cursor.fetchall()

# temp_prompt = PromptTemplate(
#     # subject, topic, subtopic
#     input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic"},
#     template="""Create related coding examples for below item :
#         subject : {subject}
#         topic : {topic}
#         subtopic : {subtopic}
#     """
# )
# query_save = """
#         UPDATE Skills
#         SET vector_tags = %s, content = %s
#         WHERE skillid = %s
# """


# chain = temp_prompt | llm
# n = len(skills)
# i = 0
# for skill_id, subject, topic, subtopic  in skills:
#     i = i+1
#     print(f"{i} / {n} {subject} {skill_id}", flush=True)
#     content = chain.invoke({"subject": subject, "topic": topic, "subtopic":subtopic})
#     vector_embedding = embeddings.embed_query(f"{subject} {topic} {subtopic} {content}")
#     cursor.execute(query_save, (vector_embedding, content, skill_id))
#     conn.commit()

# cursor.close()
# conn.close()
# subject, topic, subtopic, best_skill, performance = get_next_skill(conn, "Any")[0]
# print(subject, topic, subtopic, best_skill, performance)

subjects = [["all" , 4]]

for subject, n in subjects:
    print(subject, n)