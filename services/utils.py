import json
import re

def parse_json_output(llm_response: str):
    """
    Robustly extracts JSON from an LLM response, handling Markdown code blocks.
    """
    # 1. Try to find a code block
    if "```json" in llm_response:
        # Extract text between ```json and ```
        pattern = r"```json(.*?)```"
        match = re.search(pattern, llm_response, re.DOTALL)
        if match:
            llm_response = match.group(1)
    
    # 2. Clean whitespace
    llm_response = llm_response.strip()
    
    # 3. Parse
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        # Fallback: return a safe empty dict or error object
        return {"error": "Failed to parse JSON", "raw": llm_response}

def parse_list_output(llm_response: str) -> list:
    """
    Converts a comma-separated string into a clean list.
    """
    # Remove brackets if the LLM decided to return ["Tag1", "Tag2"]
    clean_text = llm_response.replace("[", "").replace("]", "").replace('"', '')
    
    # Split by comma and strip whitespace
    return [tag.strip() for tag in clean_text.split(",") if tag.strip()]