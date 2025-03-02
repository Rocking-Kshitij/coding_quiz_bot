import psycopg2
from chatbotconfig import embeddings, csv_folder, llm
import os
from datetime import datetime, timedelta
import pandas as pd

def get_connection(): 
    # Database connection
    conn = psycopg2.connect(
        dbname="ai_test_db",
        user="data_pgvector_user",
        password="data_pgvector_password",
        host="localhost",
        port="5435"
    )
    return conn


def setup_database(conn):
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

def get_next_skill_id(conn):
    """
    Determines the next skill ID to ask a question from based on importance, performance, and recency.
    """

    cursor = conn.cursor()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    cursor.execute(
        """
        SELECT skillid, importance, performance, updated_at
        FROM Skills
        WHERE importance > 0
        """
    )
    
    skills = cursor.fetchall()
    if not skills:
        print("No skills found.")
        return None
    
    best_skill = None
    best_score = float('-inf')

        # Weight factors
    w1, w2, w3 = 1.5, 1, 0.01
    
    for skillid, importance, performance, updated_at in skills:
        time_decay = (now - updated_at).days if updated_at else 100  # Older updates are prioritized
        score = (importance * w1) - (performance * w2) + (time_decay * w3)
        
        if score > best_score:
            best_score = score
            best_skill = skillid
    
    cursor.close()
    return best_skill

def ask_question_and_update_performance(conn, skill_id, llm):
    """
    Asks a coding question to the user, gets LLM feedback, and updates the performance in the Skills table.
    """
    cursor = conn.cursor()
    
    # Fetch skill details
    cursor.execute("SELECT subject, topic FROM Skills WHERE skillid = %s", (skill_id,))
    skill = cursor.fetchone()
    if not skill:
        print("Skill ID not found in database.")
        return
    subject, topic = skill
    
    # Generate a question using LLM
    idea_prompt = PromptTemplate(
        input_variable={"skill_name": "skill_name"},
        template="Generate a coding question for {skill_name}."
    )
    chain = idea_prompt | llm
    question = chain.invoke({"skill_name": topic})
    
    print("Question:", question)
    user_answer = input("Your answer: ")
    
    # Get LLM feedback
    feedback_prompt = PromptTemplate(
        input_variable={"question": "question", "answer": "answer"},
        template="Provide feedback and a rating (0-10) for the following answer: \n\nQuestion: {question}\nAnswer: {answer}" 
    )
    feedback_chain = feedback_prompt | llm
    feedback_response = feedback_chain.invoke({"question": question, "answer": user_answer})
    feedback, rating = feedback_response.split("Rating:")
    rating = int(rating.strip())
    
    # Store the question, answer, and feedback in the database
    embeddings = CustomEmbedding("text-embedding-nomic-embed-text-v1.5@q8_0")
    vector_data = embeddings.embed_documents([question + feedback])[0]
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
    new_performance = round((current_performance * 0.7) + (rating * 0.3), 2)
    cursor.execute(
        """
        UPDATE Skills
        SET performance = %s, updated_at = CURRENT_TIMESTAMP
        WHERE skillid = %s
        """,
        (new_performance, skill_id)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Performance updated successfully.")

last_question_vector = embeddings.embed_query("What is Python")
conn = get_connection()
# setup_database(conn)
# update_skills_from_csv(conn, embeddings, csv_folder)
skill = get_next_skill_id(conn)
print(skill)
conn.close()
