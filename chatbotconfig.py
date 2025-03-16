from lmstudio_llama import CustomLLamaLLM, CustomEmbedding
import logging
from datetime import datetime
import psycopg2
import numpy as np


# Initialize custom LLM
qwen2_5 = "qwen2.5-coder-7b-instruct"
llm = CustomLLamaLLM(llama_model=qwen2_5)
embeddings = CustomEmbedding("text-embedding-nomic-embed-text-v1.5@q8_0")


csv_folder = "csv_files"

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


# Configure logging to write logs to a file
logging.basicConfig(
    filename="llm_conversation.log",
    level=logging.INFO,
    format="%(asctime)s - User: %(message)s\n%(asctime)s - LLM: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_conversation(user_prompt, llm_response):
    """Logs the conversation between user and LLM in the correct format."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("llm_conversation.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"\n{timestamp}\nUser: {user_prompt}\nLLM: {llm_response}\n")