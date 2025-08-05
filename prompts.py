from langchain_core.prompts import PromptTemplate
from chatbotconfig import llm
import qwen2_5prompts


text_query = input("Enter the query")
vector_embedding = embeddings.embed_query(text_data)

print(vector_embedding)