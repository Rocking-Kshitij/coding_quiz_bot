from chatbotconfig import embeddings

from chatbotconfig import get_connection

conn = get_connection()
cursor = conn.cursor()


def remove_thoughts(input):
    data = input[input.rfind('</think>')+10:]
    return data

cursor.execute(
        """
        SELECT skillid, subject, topic, subtopic, content
        FROM Skills
        WHERE content LIKE '<think>%';
        """
        
)

rows = cursor.fetchall()

for skillid, subject, topic, subtopic, content in rows:
    new_content = remove_thoughts(content)
    text_data = f"{subject} {topic} {subtopic} {new_content}"
    vector_embedding = embeddings.embed_query(text_data)
    cursor.execute("""
        UPDATE Skills
        SET vector_tags = %s,
            content = %s
        WHERE skillid = %s;
    """, (vector_embedding, new_content, skillid))
    print(".", end = "", flush=True)


conn.commit()
cursor.close()
conn.close()
print("done", flush= True)