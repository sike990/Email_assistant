import json
import re

def parse_json_output(llm_response: str):
    """
    Robustly extracts JSON from an LLM response, handling Markdown code blocks and raw JSON.
    """
    if not llm_response:
        return {"error": "Empty response"}

    # 1. Try to find a code block
    if "```json" in llm_response:
        pattern = r"```json(.*?)```"
        match = re.search(pattern, llm_response, re.DOTALL)
        if match:
            llm_response = match.group(1)
    elif "```" in llm_response:
        pattern = r"```(.*?)```"
        match = re.search(pattern, llm_response, re.DOTALL)
        if match:
            llm_response = match.group(1)
    
    # 2. Clean whitespace and potential leading/trailing text
    llm_response = llm_response.strip()
    
    # 3. Try to find the first '{' and last '}' to handle non-code-block JSON
    start_idx = llm_response.find('{')
    end_idx = llm_response.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        llm_response = llm_response[start_idx:end_idx+1]
    
    # 4. Parse
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw": llm_response}

def parse_list_output(llm_response: str) -> list:
    """
    Converts a comma-separated string or JSON list into a clean list.
    """
    if not llm_response:
        return []

    # 1. Handle JSON list format ["Tag1", "Tag2"]
    if "[" in llm_response and "]" in llm_response:
        try:
            # Try to extract list part
            start = llm_response.find("[")
            end = llm_response.rfind("]")
            list_str = llm_response[start:end+1]
            return json.loads(list_str)
        except json.JSONDecodeError:
            pass # Fallback to string splitting

    # 2. Remove brackets and quotes for string splitting fallback
    clean_text = llm_response.replace("[", "").replace("]", "").replace('"', '').replace("'", "")
    
    # 3. Split by comma and strip whitespace
    return [tag.strip() for tag in clean_text.split(",") if tag.strip()]