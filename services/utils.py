import json
import re
from datetime import datetime

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

def convert_to_relative_format(date_string, reference_date=None):
    """
    Convert a datetime string to relative format like "Sat, Nov 15, 6:29 PM (9 days ago)"
    
    Args:
        date_string: Input datetime string (e.g., "2025-11-24 09:15:00")
        reference_date: Reference datetime to compare against (defaults to now)
    
    Returns:
        Formatted string with relative time
    """
    # Parse the input datetime
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    
    # Use provided reference date or current time
    if reference_date is None:
        reference_date = datetime.now()
    
    # Calculate time difference
    time_diff = reference_date - dt
    days_diff = time_diff.days
    
    # Format the date part: "Sat, Nov 15"
    formatted_date = dt.strftime("%a, %b %d")
    
    # Format the time part: "6:29 PM"
    formatted_time = dt.strftime("%I:%M %p").lstrip('0')
    
    # Determine relative time string
    if days_diff == 0:
        relative = "today"
    elif days_diff == 1:
        relative = "yesterday"
    elif days_diff > 1:
        relative = f"{days_diff} days ago"
    else:
        relative = f"in {abs(days_diff)} days"
    
    # Combine all parts
    result = f"{formatted_date}, {formatted_time} ({relative})"
    
    return result

def validate_email(email:str)->bool:
    """Validates the format of valid email and returns bool"""
    pattern = r"^[A-Za-z0-9\.\_]+[@][A-Za-z0-9\-]+[\.][A-Za-z]{2,}$"
    return True if re.search(pattern,email) else False   