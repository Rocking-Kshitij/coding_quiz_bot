import numpy as np
from chatbotconfig import llm_heavy, llm_light, get_connection, embeddings, csv_folder, log_conversation
import sqlite3, json, random, statistics
from qwen3prompts import beginner_question_chain,easy_question_chain,medium_question_chain,hard_question_chain,answer_chain, feedback_chain, rating_chain, get_question_data_chain
import pandas as pd
from datetime import datetime
import threading, time
from heapq import nlargest

get_question_created_thread = None
get_question_created_lock = threading.Lock()


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
    data = input[:input.rfind('{')+1]
    result = input[input.rfind('{'):input.rfind('}')+1]
    # result = input[input.find("{"):len(input)-input[::-1].find("}")]
    return data, json.loads(result)

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
            performance INTEGER CHECK (performance BETWEEN 0 AND 100) DEFAULT 0,
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


def get_next_skill(conn, subject, top_n=1):  # returns subject, topic
    """
    Determines the next skill ID to ask a question from based on importance, performance, and recency.
    """

    cursor = conn.cursor()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    if subject == "Any":
        cursor.execute(
            # """
            # SELECT skillid, importance, performance, updated_at
            # FROM Skills
            # WHERE importance > 0
            # """
            """
            SELECT 
            s.skillid,
            s.subject,
            s.importance AS skill_importance, 
            s.performance, 
            s.updated_at,
            si.importance AS subject_importance
            FROM Skills s
            JOIN Subject_Importance si
            ON s.subject = si.subject
            WHERE s.importance > 0
            """
        )
    else:
        cursor.execute(
            # """
            # SELECT skillid, s.importance AS skill_importance, performance, updated_at
            # FROM Skills
            # WHERE importance > 0 and subject = %s
            # """
            """
            SELECT 
            s.skillid,
            s.subject,
            s.importance AS skill_importance, 
            s.performance, 
            s.updated_at,
            si.importance AS subject_importance
            FROM Skills s
            JOIN Subject_Importance si
            ON s.subject = si.subject
            WHERE s.importance > 0 and s.subject = %s
            """,
            (subject,)
        )

    skills = cursor.fetchall()
    if not skills:
        print("No skills found.")
        return None
    else:
        random.shuffle(skills)
    sub_perf = dict()
    for skillid, subject, importance, performance, updated_at, subject_importance in skills:
        if subject not in sub_perf.keys():
            sub_perf[subject] = [0]
        if performance >0:
            sub_perf[subject].append(performance)


    
    # best_skill = None
    # best_score = float('-inf')
    top_skills = []  # Will hold tuples of (skillid, score)

        # Weight factors
    w1, w2, w3 = 0.01, 0.1, 0.05
    # imp cale -10 range 0-10
    # per scale -100 range 0-10
    #sub_imp 0-100
    #timedecay 100 days -> 10 pts
    
    for skillid, subject, importance, performance, updated_at, subject_importance in skills:
        time_decay = (now - updated_at).days if updated_at else 100  # Older updates are prioritized
        avg_sub_perf = statistics.mean(sub_perf[subject])
        score = (importance * subject_importance * w1) - (performance * w2) - (avg_sub_perf * w2)+ (time_decay * w3) + 20  # max 40 = 10 -10 -10 + 10 + 10
        top_skills.append((skillid, score))
        # if score > best_score:
        #     best_score = score
        #     best_skill = skillid

    top_skills = sorted(top_skills, key=lambda x: x[1], reverse=True)[:top_n]
    print(top_skills)

    skill_ids = [skillid for skillid, _ in top_skills]
    format_strings = ','.join(['%s'] * len(skill_ids))

    cursor.execute(f"SELECT skillid, subject, topic, subtopic, performance FROM Skills WHERE skillid IN ({format_strings})", skill_ids)
    skill = cursor.fetchall()
    
        # Fetch skill details
    # cursor.execute("SELECT subject, topic, subtopic, performance FROM Skills WHERE skillid = %s", (best_skill,))
    # skill = cursor.fetchone()
    if not skill:
        print("Skill ID not found in database.")
        return

    # print(skill)
    # subject, topic, subtopic, performance = skill
    cursor.close()
    return skill

def get_question_created(conn, subject, n_questions):
    cursor = conn.cursor()
    if subject == "All":
        cursor.execute(
            f"""
            SELECT subject, COUNT(q.question_id) AS question_count
            FROM skills s
            LEFT JOIN questionbank q ON s.skillid = q.skillid AND q.is_asked = false
            GROUP BY subject
            HAVING COUNT(q.question_id) < {n_questions};
            """     
        )
        result = cursor.fetchall()
        subjects = []
        for sub, n in result:
            subjects.append([sub, n_questions-n])
        print(subjects)
    else:
        subjects = [[subject , n_questions]]
    if subjects:
        for subject, n in subjects:
            print(f"generating for {subject}", flush = True)
            first_time = datetime.now()
            question_list = get_act_question(conn, subject, n)
            for question, best_skill, subject, topic, subtopic, level in question_list:
                answer = get_correct_answer(question)
                # data =  get_question_data(question, answer)
                vector_data = embeddings.embed_query(question + answer)
                cursor.execute(
                    """
                    INSERT INTO QuestionBank (question, vector_data, actual_answer, skillid, level)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (question, vector_data, answer, best_skill, level)
                )
                # conn.commit()
                later_time = datetime.now()
                elapsed_minutes = (later_time - first_time).total_seconds() / 60
                conn.commit()
                print(f"Time to generate question from {subject}: {elapsed_minutes:.2f} minutes", flush=True)
    cursor.close()
            
def get_question(conn, subject):
    skill = get_next_skill(conn, subject)
    best_skill, subject, topic, subtopic, performance = skill[0]
    cur = conn.cursor()
    query = """
            SELECT 
            q.question,
            q.actual_answer,
            q.skillid,
            s.subject,
            s.topic,
            s.subtopic,
            q.level,
            q.question_id
        FROM 
            questionbank q
        JOIN 
            skills s ON q.skillid = s.skillid
        WHERE 
            s.subject = %s
            AND q.is_asked = false
        LIMIT 1;
        """
    cur.execute(query, (subject,))
    result = cur.fetchone()

    if result:
        question, actual_answer, skillid, subject, topic, subtopic, level, q_id = result
    else:
        get_question_created(conn, subject, 1)
        cur.execute(query, (subject,))
        result = cur.fetchone()
        question, actual_answer, skillid, subject, topic, subtopic, level, q_id = result

    cur.close()

    return question,best_skill,subject,topic, subtopic, level, actual_answer, q_id
    #

def initiate_thread(conn):
    global get_question_created_thread
    # creating a thread for all subjects data
    cursor = conn.cursor()
    should_create = False # checks if there a subject for which there is no question ready
    cursor.execute(
            """
            SELECT subject
            FROM skills s
            LEFT JOIN questionbank q ON s.skillid = q.skillid AND q.is_asked = false
            GROUP BY subject
            HAVING COUNT(q.question_id) <= 1;
            """     
        )
    subjects = cursor.fetchall()
    cursor.close()
    if subjects:
        if len(subjects) > 0:
            print(f"Subject which need to be created {subjects} initiate_thread", flush = True)
            should_create = True
    # should_create = True # uncomment to manually trigger question creation
    # else:
    #     print(f"No need to create question", flush = True)
    with get_question_created_lock:
        if (get_question_created_thread is None or not get_question_created_thread.is_alive()) and should_create:
            print("Starting background thread", flush=True)
            get_question_created_thread = threading.Thread(target=get_question_created, args = (conn, "All", 10), daemon=True)  # conn, create for all, n question for each sub
            get_question_created_thread.start()
        # else:
        #     print("background thread is already running", flush=True)
        #     # it means thread is already running

# Function to get question from LLM based on past performance
def get_act_question(conn, subject , n):  # work to get coding language too
    skill = get_next_skill(conn, subject , n)
    questions = []
    for item in skill:
        best_skill, subject, topic, subtopic, performance = item
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
        print("question_generated", flush = True)
        questions.append([question, best_skill, subject, topic, subtopic, level])
    # question = question_chain.invoke({"subject": subject, "topic":topic, "subtopic":subtopic, "level": get_hardness(performance)})
    # log_conversation(idea_prompt, response)
    return questions


# Function to get correct answer from LLM
def get_correct_answer(question):
    response = answer_chain.invoke({"question": question})
    # log_conversation(answer_prompt, response)
    return response

def get_question_data(question, answer):
    response = get_question_data_chain.invoke({"question": question, "answer": answer})
    # log_conversation(answer_prompt, response)
    return response

def get_rating(question, user_answer):
    rating = rating_chain.invoke({"question": question, "user_answer": user_answer})
    try:
        rating = int(json.loads(rating)["rating_score"])
    except:
        feedback, rating = get_dict_result(rating)
        rating = int(rating["rating_score"])
    # feedback, rating
    # log_conversation(feedback_prompt, response)
    rating = int(min(rating *1.1, 100))
    print(rating)

    return rating

# Function to evaluate the answer
def get_feedback(question, user_answer, answer):
    feedback = feedback_chain.invoke({"question": question, "user_answer": user_answer, "answer":answer})
    return feedback

# Function to store result in the database
def store_result(conn, question, user_answer, feedback, rating, skill_id, question_id):
    # question = question.replace("\"", '\\"')
    # user_answer = user_answer.replace("\"", '\\"')
    # feedback = feedback.replace("\"", '\\"')
        # Store the question, answer, and feedback in the database
    cursor = conn.cursor()
    ## Inserting in questionbank

    cursor.execute(
        """
        UPDATE QuestionBank
        SET user_answer = %s, rating = %s, is_asked = TRUE
        where question_id = %s
        """,
        (user_answer, rating, question_id)
    )
    cursor.execute("SELECT vector_data FROM QuestionBank WHERE question_id = %s", (question_id,))
    vector_data = cursor.fetchone()[0]
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
    print(f"Updated skills {similar_skills}")
    for similar_skill_id, similar_performance, similarity in similar_skills:
        similarity_weight = max(0, 1 - similarity) * 0.3 * 0.5  # Convert distance to similarity score and limiting it to avoid large change rating * 0.3 * (0.3) last can be varied for senstivity
        updated_performance = round((similar_performance * (1 - similarity_weight)) + (rating * similarity_weight), 2)
        # updated_performance = round((similar_performance *0.7)+ ((similar_performance * (1 - similarity_weight)) + (rating * similarity_weight))*0.3, 2)
        cursor.execute(
            """
            UPDATE Skills
            SET performance = %s, updated_at = CURRENT_TIMESTAMP
            WHERE skillid = %s.
            """,
            (updated_performance, similar_skill_id)
        )
    
    conn.commit()
    cursor.close()
