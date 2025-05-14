
from chatbotconfig import embeddings, csv_folder, get_connection, llm
from langchain_core.prompts import PromptTemplate
import pandas as pd
import os

conn = get_connection()

temp_prompt = PromptTemplate(
    # subject, topic, subtopic
    input_variable={"subject": "subject", "topic":"topic", "subtopic":"subtopic"},
    template="""Create related coding examples for below item :
        subject : {subject}
        topic : {topic}
        subtopic : {subtopic}
    """
)
chain = temp_prompt | llm

done_subs = """
            SELECT distinct subject
            FROM skills
            """

def update_skills_from_csv(conn, embeddings, csv_folder):
    cursor = conn.cursor()
    cursor.execute(done_subs)
    subjects = cursor.fetchall()
    subjects = [item[0] for item in subjects]
    print(subjects, flush=True)
    for file in os.listdir(csv_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(csv_folder, file)
            print(file_path, flush=True)
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                if row['subject'] in subjects:
                    break
                content = chain.invoke({"subject": row['subject'], "topic": row['topic'], "subtopic":row.get('subtopic', '')})
                text_data = f"{row['subject']} {row['topic']} {row.get('subtopic', '')} {content}"
                vector_embedding = embeddings.embed_query(text_data)
                
                cursor.execute(
                    """
                    INSERT INTO Skills (subject, topic, subtopic, importance, performance, vector_tags, content)
                    VALUES (%s, %s, %s, %s, 0, %s, %s)
                    ON CONFLICT (subject, topic, subtopic) DO UPDATE 
                    SET importance = EXCLUDED.importance,
                        updated_at = CURRENT_TIMESTAMP,
                        vector_tags = EXCLUDED.vector_tags;
                    """,
                    (row['subject'], row['topic'], row.get('subtopic', None), row['importance'], vector_embedding, content)
                )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Skills table updated from CSV files.")


update_skills_from_csv(conn, embeddings, csv_folder)