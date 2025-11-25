from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from services.utils import parse_json_output, parse_list_output

# Load environment variables (API keys)
load_dotenv()

def process_email(email_body: str, instruction_text: str, temperature: float = 1.0):
    """
    Generic function to process an email with a given instruction.
    Useful for ad-hoc queries or tasks not covered by specific functions.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=api_key,
        temperature=temperature
    )
    
    # Simple prompt structure for generic tasks
    chain_prompt = PromptTemplate.from_template(
        """{instruction_text} \n\n === EMAIL CONTENT === \n {email_body} ===NOTE===\n Do not add any preamble or explanation. Just give the asked output"""
    )
    
    email_model = chain_prompt | llm
    response = email_model.invoke(input={"email_body": email_body, "instruction_text": instruction_text})
    return response.content 

def categorize_email(email_body: str, user_instructions: str = "") -> list:
    """
    Categorizes an email based on its content and user-defined definitions.
    
    We use a strict prompt here to ensure the LLM returns a clean, comma-separated list
    of tags, which makes parsing much more reliable than free-form text.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    # Using a lower temperature for more deterministic categorization
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=api_key,
        temperature=0.0
    )
    
    prompt = PromptTemplate.from_template(
        """
        ### INSTRUCTION:
        Categorize the following email into one or more of the categories using the user instructions.
        
        ### USER INSTRUCTIONS:
        {user_instructions}
        
        ### FORMAT (HIGHEST PRIORITY):
        Return ONLY a comma-separated list of tags. Do not add any preamble or explanation.
        Example: Important, To-Do
        
        ### EMAIL CONTENT:
        {email_body}
        
        ### OUTPUT:
        """
    )
    
    chain = prompt | llm
    response = chain.invoke(input={"email_body": email_body, "user_instructions": user_instructions})
    
    # Parse the output into a clean list of strings
    return parse_list_output(response.content)

def extract_action_items(email_body: str, user_instructions: str = "") -> dict:
    """
    Extracts actionable tasks and deadlines from an email.
    
    Returns a dictionary with 'task' and 'deadline' keys. We force the LLM to output 
    JSON to ensure we can programmatically use the results in the UI.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=api_key,
        temperature=0.0
    )
    
    prompt = PromptTemplate.from_template(
        """
        ### INSTRUCTION:
        Extract actionable tasks and deadlines from the email using the user instructions.
        
        ### USER INSTRUCTIONS:
        {user_instructions}
        
        ### FORMAT (HIGHEST PRIORITY):
        Respond strictly in JSON format with the following structure:
        {{
          "task": "Description of the task",
          "deadline": "Date/Time or 'None'"
        }}
        
        If there are no clear tasks, return:
        {{
          "task": "None",
          "deadline": "None"
        }}
        
        ### EMAIL CONTENT:
        {email_body}
        
        ### JSON OUTPUT:
        """
    )
    
    chain = prompt | llm
    response = chain.invoke(input={"email_body": email_body, "user_instructions": user_instructions})
    
    # Robustly parse the JSON response, handling potential formatting issues
    return parse_json_output(response.content)

def generate_auto_reply(email_body: str, user_instructions: str = "") -> str:
    """
    Generates a professional, context-aware reply to an email.
    
    The output is a raw string ready to be pasted into a draft. We explicitly ask 
    the LLM to avoid JSON or quotes here so it feels like a natural email draft.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    # Slightly higher temperature for more creative/natural writing
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0.7
    )
    
    prompt = PromptTemplate.from_template(
        """
        ### INSTRUCTION:
        Draft a professional and context-aware reply to the following email.
        
        ### USER INSTRUCTIONS:
        {user_instructions}
        
        ### FORMAT (HIGHEST PRIORITY):
        Return ONLY the body of the reply as a raw string. 
        Do NOT wrap it in JSON. 
        Do NOT wrap it in quotes.
        Do NOT add any preamble like "Here is the draft:".
        Just start with the salutation (e.g., "Dear Name,").
        
        ### EMAIL CONTENT:
        {email_body}
        
        ### DRAFT REPLY:
        """
    )
    
    chain = prompt | llm
    response = chain.invoke(input={"email_body": email_body, "user_instructions": user_instructions})
    return response.content 

def process_global_query(emails: list, query: str, chat_history: list = [], temperature: float = 1.0) -> str:
    """
    Answers questions about the entire inbox, taking into account recent chat history.
    
    This function aggregates email content (currently all of it, but could be summarized)
    and feeds it to the LLM along with the user's query and conversation context.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq API Key is absent")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=temperature
    )
    
    # Prepare the inbox context. In a production app, we might need to summarize 
    # or retrieve only relevant emails to fit within the context window.
    inbox_context = ""
    for email in emails:
        inbox_context += f"ID: {email.get('id')}\nFrom: {email.get('name')} <{email.get('sender')}>\nSubject: {email.get('subject')}\nBody: {email.get('body')}\nTags: {email.get('tags')}\nAction Item: {email.get('action_item')} \n is_read:{email.get('is_read')}\n\n\n"

    # Format chat history for the prompt
    formatted_history = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['message']}\n"

    prompt_template = PromptTemplate.from_template(
        """You are an intelligent email assistant. You have access to the user's inbox.
        
        === INBOX CONTENT ===
        {inbox_context}
        
        === CHAT HISTORY ===
        {chat_history}
        
        === USER QUERY ===
        {query}
        
        Answer the user's query based on the inbox content and chat history (ignore history if irrelevant). Be concise and helpful.
        """
    )
    
    chain = prompt_template | llm
    response = chain.invoke(input={"inbox_context": inbox_context, "chat_history": formatted_history, "query": query})
    return response.content

def generate_draft(prompt: str, recipient: str, recipient_email: str, subject: str, temperature: float = 1.0) -> str:
    """
    Generates a fresh email draft from scratch based on a user prompt.
    """
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
        Recipient Name (Optional): {recipient}
        Recipient Email: {recipient_email}
        Subject: {subject}
        
        ### Instructions/Context:
        {prompt}
        
        ### Format (Highest Priority):
        Return ONLY the body of the email in the raw string format. Do not include the subject line or any preamble.
        
        ### Output:
        """
    )
    
    chain = prompt_template | llm
    response = chain.invoke(input={"recipient": recipient, "recipient_email": recipient_email, "subject": subject, "prompt": prompt})
    return response.content

