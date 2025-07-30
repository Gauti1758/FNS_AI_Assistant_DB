import pickle
from core.models import DatabaseSchema
from pathlib import Path
import os

def save_schema(schema, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        pickle.dump(schema, f)


def load_schema(filepath: str) -> DatabaseSchema:
    with open(filepath, "rb") as f:
        return pickle.load(f)