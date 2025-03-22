from langchain_core.prompts import PromptTemplate
from chatbotconfig import llm

# Generate a question using LLM
# question_prompt = PromptTemplate(
#     # subject, topic, subtopic
#     input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
#     template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
#     Topic: {topic}
#     Subtopic: {subtopic}
#     Note that
#     1. question should ask to write a code for certain problem. 
#     2. Question should primarily be testing knowledge of provided Topic and Subtopic.
#     3. Question must be clear, concise and easy to understand.
#     4. Question must include all the required data to solve it.
#     5. Question should not include examples, snippets and unnecessary hints.
#     6. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
#     """
# )
# question_chain = question_prompt | llm

beginner_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. question should ask to write a code for certain problem of {level}.
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question must be clear, concise and easy to understand.
    4. Question must include all the required data to solve it.
    5. Question should include examples, snippets, assistance and hints required for a noob to solve the question.
    6. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    """
)
beginner_question_chain = beginner_question_prompt | llm

easy_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. question should ask to write a code for certain problem. 
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question must be clear, concise and easy to understand.
    4. Question must include all the required data to solve it.
    5. Question should not include examples, snippets and unnecessary hints.
    6. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    """
)
easy_question_chain = easy_question_prompt | llm

medium_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. question should ask to write a code for certain problem. 
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question must be clear, concise and easy to understand.
    4. Question must include all the required data to solve it.
    5. Question should not include examples, snippets and unnecessary hints.
    6. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    """
)
medium_question_chain = medium_question_prompt | llm

hard_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. question should ask to write a code for certain problem. 
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question must be clear, concise and easy to understand.
    4. Question must include all the required data to solve it.
    5. Question should not include examples, snippets and unnecessary hints.
    6. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    """
)
hard_question_chain = hard_question_prompt | llm

# Language_Prompt = PromptTemplate(
#     Also tell the coding language to be used in the answer like python / bash / sql / yaml / HashiCorp Configuration Language etc:
#     Output should only be the json format as mentioned below:
#     "Question" : "Coding Question",
#     "Language": "Coding language"
# )

answer_prompt = PromptTemplate(
    # question
    input_variable={"question": "question"},
    template="""Provide the correct answer for the following question in detailed and easy to easy to understand manner:
    {question}"""
)
answer_chain = answer_prompt | llm

feedback_prompt = PromptTemplate(
    input_variable={"question": "question", "user_answer": "user_answer"},
    template = """Evaluate the following answer for the given question. Provide detailed feedback including correctness, improvements, and best practices.
    Provide the correct answer for the following question in detailed and easy to easy to understand manner

    Question: {question}

    Answer: {user_answer}
    """
)
feedback_chain = feedback_prompt | llm

rating_prompt = PromptTemplate(
    input_variable={"question": "question", "user_answer": "user_answer", "feedback":"feedback"},
    template = """Provide the rating to user based on his answer in range 0-100. Dont use decimal digits (Whole Numbers only). No knowledge means 0 and perfect answer means 100.
    Question was : {question}
    This was the feedback already provided to user : {feedback}
    This was the user's answer: {user_answer}
    Your Output should only be the json format as mentioned below:
    {
    "rating_score":"Score to user in range (0-100) according to the output provided."
    }
    """
)

rating_chain = rating_prompt | llm