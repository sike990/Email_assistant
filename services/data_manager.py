import json
import os
from pathlib import Path


# Define the base directory for data storage relative to this file
BASE_DIR = Path(__file__).resolve().parents[1] / "data"


def load_payload(relfile: str) -> dict:
    """
    Reads a JSON file from the 'data' directory and returns it as a Python object.
    
    Args:
        relfile: The filename relative to the 'data' directory (e.g., 'mock_inbox.json').
        
    Returns:
        dict or list: The parsed JSON content. Returns empty structure if file is missing or invalid.
    """
    pathfile = BASE_DIR / relfile
    try:
        with open(pathfile, 'r', encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                # Return list for compose/drafts, dict for others (defaulting logic)
                return [] if "compose" in relfile else {}
            data = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fail gracefully by returning empty structures
        return [] if "compose" in relfile else {}
    return data

def save_data(relfile: str, data) -> None:
    """
    Writes data to a JSON file in the 'data' directory.
    
    Args:
        relfile: The target filename.
        data: The Python object (dict/list) to serialize.
    """
    pathfile = BASE_DIR / relfile 
    
    # Ensure the directory exists
    pathfile.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pathfile, 'w', encoding="utf-8") as f:
        # Use indent=2 for human-readable JSON files
        json.dump(data, f, indent=2, ensure_ascii=False)
    



