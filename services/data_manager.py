import json
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1] / "data"


def load_payload(relfile:str) -> dict:
    """Reads json file from the path and returns json object"""
    pathfile = BASE_DIR / relfile
    data = None
    with open(pathfile , 'r' , encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_data(relfile : str , data) -> None:
    """Writes the data to the data/relpath file"""
    pathfile = BASE_DIR / relfile 
    pathfile.parent.mkdir(parents = True , exist_ok = True)
    with open(pathfile , 'w' , encoding="utf-8") as f:
        json.dump(data, f, indent = 2, ensure_ascii = False)
    



