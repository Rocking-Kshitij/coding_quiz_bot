from chatbotconfig import get_connection
from chat_bot_backend import get_question, get_dict_result
import time, json


# conn = get_connection()
# # verify_question_created(conn)
# subject = "FastAPI"
# question, skill_id, subject, topic, subtopic, level, answer = get_question(conn, subject)
# for item in [question, skill_id, subject, topic, subtopic, level, answer]:
#     print(item)
#     print("---------------------------------------")
#     time.sleep(10)



rating = """
adjhsfgdfjhbgfjh{
    "rating_score":"75"
}dfgdkgfh
"""
# data = rating[:rating.rfind('{')]
# result = rating[rating.rfind('{'):rating.rfind('}')+1]
# result = int(json.loads(result)["rating_score"])

# print(data)
# print("----")
# print(result)
try:
    rating = int(json.loads(rating)["rating_score"])
except:
    print("got error while fetching feedback and rating")
    print(rating)
    feedback, rating = get_dict_result(rating)
    # rating = int(json.loads(rating)["rating_score"])
    print(feedback)
print("---------")
print(rating["rating_score"])