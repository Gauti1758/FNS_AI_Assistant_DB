import pickle
from datetime import datetime

def load_schema(filepath):
    with open(filepath, "rb") as file:
        return pickle.load(file)

if __name__ == "__main__":
    schema = load_schema("metadata/database_schema.pkl")

    print(f"\n📅 Extracted At: {datetime.now()}")
    print("📦 Raw Extracted Schema:\n")

    # Print raw dict-like structure
    import pprint
    pprint.pprint(schema, width=120)
