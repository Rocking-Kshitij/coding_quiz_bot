import streamlit as st
import json
from lmstudio_llama import CustomLLamaLLM
from langchain_core.prompts import PromptTemplate

llama_model3b = "llama-3.2-3b-instruct"
# llama_model1b = "llama-3.2-1b-instruct"
llm = CustomLLamaLLM(llama_model = llama_model3b)

idea_prompt = PromptTemplate(
    input_variable = {"skill_name":"skill_name", "skill_level":"skill_level"},
    template = "Generate a coding question for someone with {skill_level} expertise in {skill_name}."
)

n= input("Enter your skill level")
skill_name = input("Enter your skill name")
chain = idea_prompt | llm
result = chain.invoke({"skill_name":skill_name, "skill_level":n})

print(result)