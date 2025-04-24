
from chatbotconfig import embeddings, csv_folder, get_connection
import pandas as pd
import os

conn = get_connection()

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
                    INSERT INTO Skills (subject, topic, subtopic, importance, performance, vector_tags)
                    VALUES (%s, %s, %s, %s, 0, %s)
                    ON CONFLICT (subject, topic, subtopic) DO UPDATE 
                    SET importance = EXCLUDED.importance,
                        updated_at = CURRENT_TIMESTAMP,
                        vector_tags = EXCLUDED.vector_tags;
                    """,
                    (row['subject'], row['topic'], row.get('subtopic', None), row['importance'], vector_embedding)
                )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Skills table updated from CSV files.")


update_skills_from_csv(conn, embeddings, csv_folder)