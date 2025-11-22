from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

load_dotenv()
def get_llm_response(prompt:str = "Why do we fall?[A Philosopy question]" , temperature:float = 1.0) -> str:
    """Returns llm response for prompts"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model = "llama-3.3-70b-versatile",
        groq_api_key = api_key,
        temperature = temperature
    )
    response = llm.invoke(prompt)
    return response.content




def process_email(email_body:str , instruction_text:str , temperature:float = 0.7):
    """Returns llm response for prompts"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model = "llama-3.1-8b-instant",
        groq_api_key = api_key,
        temperature = temperature
    )
    chain_prompt = PromptTemplate.from_template(
        """{instruction_text} \n\n === EMAIL CONTENT === \n {email_body}"""
    )
    email_model = chain_prompt | llm
    response = email_model.invoke(input = {"email_body" : email_body , "instruction_text" : instruction_text})
    return response.content 

