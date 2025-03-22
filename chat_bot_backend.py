import numpy as np
from chatbotconfig import llm, get_connection, embeddings, csv_folder, log_conversation
import sqlite3, json, random
from prompts import beginner_question_chain,easy_question_chain,medium_question_chain,hard_question_chain,answer_chain, feedback_chain, rating_chain
import pandas as pd
from datetime import datetime

# def remove_extra(str):
#     return str.replace("\"", '\\"')
# conn = get_connection()
def get_hardness(score):
    score = int(score)
    if score <25:
        return "Beginner level"
    elif score <50:
        return "Easy level"
    elif score <75:
        return "Medium level"
    else:
        return "Hard Level"

# getting json
def get_dict_result(input):
    result = input[input.find("{"):len(input)-input[::-1].find("}")]
    return json.loads(result)

# Database setup  #now
def setup_database(conn):  # now
    cursor = conn.cursor()
    # Enable pgvector extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Create Skills table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Skills (
            skillid SERIAL PRIMARY KEY,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            subtopic TEXT,
            content TEXT,
            importance INTEGER CHECK (importance BETWEEN 0 AND 10),
            performance INTEGER CHECK (performance BETWEEN 0 AND 10) DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vector_tags vector(768),
            UNIQUE (subject, topic, subtopic)
        );
        """
    )
    
    # Create QuestionBank table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS QuestionBank (
            question_id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            user_answer TEXT,
            feedback TEXT,
            rating INTEGER CHECK (rating BETWEEN 0 AND 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vector_data vector(768)
        );
        """
    )
    
    conn.commit()
    cursor.close()
    print("Database setup complete.")

def update_skills_from_csv(conn, embeddings, csv_folder):
    cursor = conn.cursor()
    
    for file in os.listdir(csv_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(csv_folder, file)
            print(file_path, flush=True)
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                text_data = f"{row['subject']} {row['topic']} {row.get('subtopic', '')} {row.get('content', '')}"
                vector_embedding = embeddings.embed_query(text_data)
                
                cursor.execute(
                    """
                    INSERT INTO Skills (subject, topic, subtopic, content, importance, performance, vector_tags)
                    VALUES (%s, %s, %s, %s, %s, 0, %s)
                    ON CONFLICT (subject, topic, subtopic) DO UPDATE 
                    SET content = EXCLUDED.content,
                        importance = EXCLUDED.importance,
                        updated_at = CURRENT_TIMESTAMP,
                        vector_tags = EXCLUDED.vector_tags;
                    """,
                    (row['subject'], row['topic'], row.get('subtopic', None), row.get('content', None), row['importance'], vector_embedding)
                )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Skills table updated from CSV files.")


def get_next_skill(conn, subject):  # returns subject, topic
    """
    Determines the next skill ID to ask a question from based on importance, performance, and recency.
    """

    cursor = conn.cursor()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    if subject == "Any":
        cursor.execute(
            """
            SELECT skillid, importance, performance, updated_at
            FROM Skills
            WHERE importance > 0
            """
        )
    else:
        cursor.execute(
            """
            SELECT skillid, importance, performance, updated_at
            FROM Skills
            WHERE importance > 0 and subject = %s
            """,
            (subject,)
        )

    skills = cursor.fetchall()
    if not skills:
        print("No skills found.")
        return None
    else:
        random.shuffle(skills)
    
    best_skill = None
    best_score = float('-inf')

        # Weight factors
    w1, w2, w3 = 1.5, 0.1, 0.01
    
    for skillid, importance, performance, updated_at in skills:
        time_decay = (now - updated_at).days if updated_at else 100  # Older updates are prioritized
        score = (importance * w1) - (performance * w2) + (time_decay * w3)
        
        if score > best_score:
            best_score = score
            best_skill = skillid
    
        # Fetch skill details
    cursor.execute("SELECT subject, topic, subtopic, performance FROM Skills WHERE skillid = %s", (best_skill,))
    skill = cursor.fetchone()
    if not skill:
        print("Skill ID not found in database.")
        return
    subject, topic, subtopic, performance = skill
    cursor.close()
    return subject, topic, subtopic, best_skill, performance

# Function to get question from LLM based on past performance
def get_question(conn, subject):  # work to get coding language too
    subject, topic, subtopic, best_skill, performance = get_next_skill(conn, subject)
    score = int(performance)
    if score <25:
        level = "Beginner level"
        question = beginner_question_chain.invoke({"subject": subject, "topic":topic, "subtopic":subtopic, "level": level})
    elif score <50:
        level = "Easy level"
        question = easy_question_chain.invoke({"subject": subject, "topic":topic, "subtopic":subtopic, "level": level})
    elif score <75:
        level = "Medium level"
        question = medium_question_chain.invoke({"subject": subject, "topic":topic, "subtopic":subtopic, "level": level})
    else:
        level = "Hard level"
        question = hard_question_chain.invoke({"subject": subject, "topic":topic, "subtopic":subtopic, "level": level})
    # question = question_chain.invoke({"subject": subject, "topic":topic, "subtopic":subtopic, "level": get_hardness(performance)})
    # log_conversation(idea_prompt, response)
    return question, best_skill, subject, topic, subtopic, level


# Function to get correct answer from LLM
def get_correct_answer(question):
    response = answer_chain.invoke({"question": question})
    # log_conversation(answer_prompt, response)
    return response

# Function to evaluate the answer
def get_feedback(question, user_answer):
    feedback = feedback_chain.invoke({"question": question, "user_answer": user_answer})
    try:
        rating = rating_chain.invoke({"question": question, "user_answer": user_answer, "feedback": feedback})
    except:
        rating = rating_chain.invoke({"question": question, "user_answer": user_answer, "feedback": feedback})
    rating_json = get_dict_result(rating)
    # feedback, rating
    # log_conversation(feedback_prompt, response)
    return feedback, int(rating_json["rating_score"])

# Function to store result in the database
def store_result(conn, question, user_answer, feedback, rating, skill_id):
    # question = question.replace("\"", '\\"')
    # user_answer = user_answer.replace("\"", '\\"')
    # feedback = feedback.replace("\"", '\\"')
        # Store the question, answer, and feedback in the database
    vector_data = embeddings.embed_documents([question + feedback])[0]
    cursor = conn.cursor()
    ## Inserting in questionbank
    cursor.execute(
        """
        INSERT INTO QuestionBank (question, user_answer, feedback, rating, vector_data)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (question, user_answer, feedback, rating, vector_data)
    )
    # Update performance in the Skills table using weighted average
    cursor.execute("SELECT performance FROM Skills WHERE skillid = %s", (skill_id,))
    current_performance = cursor.fetchone()[0]
    #70% weight is given to the current performance in the skills table. 30% weight is assigned to the new rating received from the LLM.
    new_performance = round((current_performance * 0.9) + (rating * 0.1), 2)
    cursor.execute(
        """
        UPDATE Skills
        SET performance = %s, updated_at = CURRENT_TIMESTAMP
        WHERE skillid = %s
        """,
        (new_performance, skill_id)
    )
    # Update performance for other similar skills using vector similarity
    cursor.execute(
        """
        SELECT skillid, performance, vector_tags <=> %s::vector AS similarity
        FROM Skills
        WHERE skillid != %s
        ORDER BY similarity ASC
        LIMIT 5  -- Consider top 5 most similar topics
        """,
        (vector_data, skill_id)
    )

    similar_skills = cursor.fetchall()
    
    for similar_skill_id, similar_performance, similarity in similar_skills:
        similarity_weight = max(0, 1 - similarity)  # Convert distance to similarity score
        updated_performance = round((similar_performance * (1 - similarity_weight)) + (rating * similarity_weight), 2)
        cursor.execute(
            """
            UPDATE Skills
            SET performance = %s, updated_at = CURRENT_TIMESTAMP
            WHERE skillid = %s
            """,
            (updated_performance, similar_skill_id)
        )
    
    conn.commit()
    cursor.close()
