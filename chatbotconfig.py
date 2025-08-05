from lmstudio_llama import CustomLLamaLLM, CustomEmbedding, OllamaCustomLLamaLLM, OllamaCustomFastAPILLM
import logging
from datetime import datetime
import psycopg2, os
import numpy as np


# Initialize custom LLM
qwen2_5_7b = "qwen2.5-coder-7b-instruct"
qwen2_5_14b = "qwen2.5-coder-14b-instruct"
deepseek_r1 = "deepseek-r1-distill-qwen-7b"
deepseek_r1 = "deepseek-r1-distill-qwen-7b"
qwen3_8b = "qwen3-8b"
ollama_qwen3_30b = "qwen3:30b"
llm_heavy = OllamaCustomFastAPILLM(model = ollama_qwen3_30b, url = "https://t8bl3bx19cn88b-8000.proxy.runpod.net/ask", sleep_time=15)
# llm_heavy = OllamaCustomLLamaLLM(model = ollama_qwen3_30b, url = "https://2orwypq8zgt3tk-11434.proxy.runpod.net")
llm_light = CustomLLamaLLM(llama_model=qwen3_8b)
# embeddings = CustomEmbedding("text-embedding-nomic-embed-text-v1.5@q8_0")
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
