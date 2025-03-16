from langchain_core.prompts import PromptTemplate
from chatbotconfig import llm

# Generate a question using LLM
question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic"},
    template="""Generate a coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that question should ask to write a code for certain problem
    """
)
question_chain = question_prompt | llm

# Language_Prompt = PromptTemplate(
#     Also tell the coding language to be used in the answer like python / bash / sql / yaml / HashiCorp Configuration Language etc:
#     Output should only be the json format as mentioned below:
#     "Question" : "Coding Question",
#     "Language": "Coding language"
# )

answer_prompt = PromptTemplate(
    # question
    input_variable={"question": "question"},
    template="""Provide the correct answer for the following question:
    {question}"""
)
answer_chain = answer_prompt | llm

feedback_prompt = PromptTemplate(
    input_variable={"question": "question", "user_answer": "user_answer"},
    template = """Evaluate the following answer for the given question. Provide detailed feedback including correctness, improvements, and best practices.

    Question: {question}

    Answer: {user_answer}
    """
)
feedback_chain = feedback_prompt | llm

rating_prompt = PromptTemplate(
    input_variable={"question": "question", "user_answer": "user_answer", "feedback":"feedback"},
    template = """Provide the rating to user based on his answer in range 0-10. Dont use decimal digits (Whole Numbers only). No knowledge means 0 and perfect answer means 10.
    Question was : {question}
    This was the feedback already provided to user : {feedback}
    This was the user's answer: {user_answer}
    Your Output should only be the json format as mentioned below:
    "rating_score":"Score to user in range (0-10) according to the output provided."
    """
)

rating_chain = rating_prompt | llm