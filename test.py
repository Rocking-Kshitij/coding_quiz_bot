from lmstudio_llama import CustomEmbedding

embeddings = CustomEmbedding("text-embedding-nomic-embed-text-v1.5@q8_0")

# print(embeddings.embed_documents(["hello", "bye"]))
print(len(embeddings.embed_query("hiee")))

# embedding vector length = 768