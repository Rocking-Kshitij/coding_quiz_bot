from langchain_core.prompts import PromptTemplate
from chatbotconfig import llm_heavy, llm_light

def remove_thoughts(input):
    data = input[input.rfind('</think>')+10:]
    return data

beginner_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. Question should ask to write a code for certain problem of {level}.
    2. Question should primarily be for testing knowledge of provided Topic and Subtopic.
    3. Question doesnt require to test all the concepts. If there are multiple concepts then test any / combination of the concept as suitable.
    4. Question must be absolutely correct, clear, concise and easy to understand.
    5. Question must include all the required data to solve it. Example urls, file paths etc should be clearly stated.
    6. Current scenerio/situation in the question should be explained in complete, concise and pointwise language.
    7. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    8. Also Provide complete answer with comments explained for user to take assistance from.
    9. Include Explanation of topic in correct, clear, concise and easy to understand language.
    """
)

easy_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. Question should ask to write a code for certain problem of {level}.
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question doesnt require to test all the concepts. If there are multiple concepts then test any / combination of the concept as suitable.
    4. Question must be clear, concise and easy to understand.
    5. Question must include all the required data to solve it. Current scenerio/situation should be explained in detail.
    6. Question should include examples, snippets, assistance and hints required to solve the question but shouldnt include complete answer.
    7. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    8. Provide required boilerplate to the user.
    """
)

medium_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. question should ask to write a code for certain problem of {level}.
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question doesnt require to test all the concepts. If there are multiple concepts then test any / combination of the concept as suitable.
    4. Question must be clear, concise and easy to understand.
    5. Question must include all the required data to solve it.
    6. Question should not include examples, snippets. Question may contain required and necessary hints.
    7. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    8. Provide required boilerplate to the user.
    """
)

hard_question_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic", "level": "level"},
    template="""Generate a {level} coding question for a coding contest for {subject} belonging to:
    Topic: {topic}
    Subtopic: {subtopic}
    Note that
    1. question should ask to write a code for certain problem of {level}.
    2. Question should primarily be testing knowledge of provided Topic and Subtopic.
    3. Question doesnt require to test all the concepts. If there are multiple concepts then test any / combination of the concept as suitable.
    4. Question must be clear, concise and easy to understand.
    5. Question must include all the required data to solve it.
    6. Question should not include examples, snippets and unnecessary hints.
    7. Note that the user is provided a single page IDE to write the code. Question should be asked accordingly to be answered in a single file.
    8. Provide required boilerplate to the user.
    """
)

answer_prompt = PromptTemplate(
    # question
    input_variable={"question": "question"},
    template="""Provide the correct answer for the following question in detailed and easy to easy to understand manner:
    {question}"""
)

get_question_data_prompt = PromptTemplate(
    input_variable = {"question": "question", "answer": "answer"},
    template = """Provide all the Data required by user in one place while coding the solution. Only include the data in clear and concise format.
    <Asked Question start here tag>
    {question}
    <Asked Question ends here tag>

    <Expected answer to the question starts here tag>
    {answer}
    <<Expected answer to the question ends here tag>

    Aggregate the Data required by the user in concise organised format to solve the above question for the correct answer.
    The Data can include:
        1. Links/ folder paths
        2. variables names to be used.
        3. any specific details about the question
        4. shouldnt include specific syntax details / commands details
        etc
    /no_think"""
)

feedback_prompt = PromptTemplate(
    input_variable={"question": "question", "user_answer": "user_answer", "answer":"answer"},
    template = """Evaluate the following answer for the given question. Provide brief feedback including correctness, improvements, and best practices.
Note that:
1) Correct answer has already been provided to user as feedback
2) Ignore slight syntax mistakes like spaces, slight misspells, slight bracket misallignment, not providing comments etc.
3) Provide the feedback in Short 2-3 lines only.
<Asked Question start here tag>
{question}
<Asked Question ends here tag>
<expected answer start here tag>
{answer}
<expected answer start here tag>
<user answer start here tag>
{user_answer}
<user answer ends here tag>
/no_think"""
)

rating_prompt = PromptTemplate(
    # input_variable={"question": "question", "user_answer": "user_answer"},
    input_variable={"question": "question", "user_answer": "user_answer"},
    template = """Provide the rating to user based on his answer in range 0-100. Dont use decimal digits (Whole Numbers only). No knowledge means 0 and correct answer means 100.
    If the answer is correct and satisfactory then rating_score should be 100.

    <Asked Question start here tag>
    Question was : {question}
    <Asked Question ends here tag>

    <user answer start here tag>
    {user_answer}
    <user answer ends here tag>
    
    Note that:
    1) Analyze the question and the answer and provide the rating to the answer in range 0-100 accordingly.
    2) No knowledge and complete knowledge gap means 0 rating and satisfactory and correct answer means 100.
    3) Rating should reflect the grasp of user on the concept from 0-100.
    4) Ignore slight syntax mistakes like spaces, slight misspells, slight bracket misallignment, not providing comments etc.
    Your Output should only be the json format as mentioned below:
    {{
    "rating_score":"Score to user in range (0-100) according to the output provided."
    }}
/no_think"""
        # This was the feedback already provided to user : {feedback}
)


beginner_question_chain = beginner_question_prompt | llm_heavy | remove_thoughts


easy_question_chain = easy_question_prompt | llm_heavy | remove_thoughts


medium_question_chain = medium_question_prompt | llm_heavy | remove_thoughts


hard_question_chain = hard_question_prompt | llm_heavy | remove_thoughts


answer_chain = answer_prompt | llm_heavy | remove_thoughts



get_question_data_chain = get_question_data_prompt | llm_light | remove_thoughts

feedback_chain = feedback_prompt | llm_light | remove_thoughts


rating_chain = rating_prompt | llm_light | remove_thoughts