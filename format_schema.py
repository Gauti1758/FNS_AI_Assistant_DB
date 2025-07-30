# modules/format_schema.py

import pickle
import json
from pathlib import Path
from core.models import DatabaseSchema

def load_schema_from_pickle(pickle_path: str) -> DatabaseSchema:
    with open(pickle_path, 'rb') as f:
        return pickle.load(f)

def format_schema_to_json(schema: DatabaseSchema) -> dict:
    structured = {}

    for full_table_name, table_info in schema.tables.items():
        schema_name = table_info.schema_name
        table_name = table_info.table_name

        if schema_name not in structured:
            structured[schema_name] = {"tables": {}}
        
        structured[schema_name]["tables"][table_name] = {"columns": []}

        for col in table_info.columns:
            column_data = {
                "name": col.column_name,
                "data_type": col.data_type,
                "is_primary_key": col.is_primary_key,
                "is_foreign_key": col.is_foreign_key,
                "references": {
                    "schema": col.foreign_key_info.referenced_table_schema,
                    "table": col.foreign_key_info.referenced_table_name,
                    "column": col.foreign_key_info.referenced_column_name
                } if col.foreign_key_info else None,
                "synonyms": []  # to be extended later
            }
            structured[schema_name]["tables"][table_name]["columns"].append(column_data)

    return {"schemas": structured}

def save_json(data: dict, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✅ LLM-ready schema saved to {filepath}")

if __name__ == "__main__":
    pickle_path = "metadata/database_schema.pkl"
    output_path = "data/llm_schema.json"

    schema = load_schema_from_pickle(pickle_path)
    json_data = format_schema_to_json(schema)
    save_json(json_data, output_path)
