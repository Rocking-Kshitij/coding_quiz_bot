
import numpy as np
from chatbotconfig import llm, log_conversation, db_name
import sqlite3




# Database setup
def init_db():
    conn = sqlite3.connect(db_name)
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
    conn = sqlite3.connect(db_name)
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
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO practice (question, user_answer, feedback, difficulty, skill_name, subtopic) VALUES (?, ?, ?, ?, ?, ?)",
              (question, user_answer, feedback, difficulty, skill_name, subtopic))
    conn.commit()
    conn.close()
