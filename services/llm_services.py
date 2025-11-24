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




def process_email(email_body:str , instruction_text:str , temperature:float = 1.0):
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

def process_global_query(emails: list, query: str, temperature: float = 1) -> str:
    """Processes a query against the entire inbox context."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=temperature
    )
    
    # Summarize emails to fit context if needed, for now we dump them all
    # In a real app, we might need to truncate or use a map-reduce approach
    inbox_context = ""
    for email in emails:
        inbox_context += f"ID: {email.get('id')}\nFrom: {email.get('name')} <{email.get('sender')}>\nSubject: {email.get('subject')}\nBody: {email.get('body')}\nTags: {email.get('tags')}\n\n"

    prompt_template = PromptTemplate.from_template(
        """You are an intelligent email assistant. You have access to the user's inbox.
        
        === INBOX CONTENT ===
        {inbox_context}
        
        === USER QUERY ===
        {query}
        
        Answer the user's query based on the inbox content. Be concise and helpful.
        """
    )
    
    chain = prompt_template | llm
    response = chain.invoke(input={"inbox_context": inbox_context, "query": query})
    return response.content

def generate_draft(prompt: str, recipient:str, recipient_email: str, subject: str, temperature: float = 1.0) -> str:
    """Generates a new email draft based on a prompt."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=temperature
    )
    
    prompt_template = PromptTemplate.from_template(
        """You are an intelligent email assistant. Draft a professional email based on the following details:
        Recipient Name(Optional): {recipient}
        Recipient email: {recipient_email}
        Subject: {subject}
        
        Instructions/Context:
        {prompt}
        
        Return ONLY the body of the email. Do not include the subject line or any preamble.
        """
    )
    
    chain = prompt_template | llm
    response = chain.invoke(input={"recipient": recipient,"recipient_email": recipient_email, "subject": subject, "prompt": prompt})
    return response.content

