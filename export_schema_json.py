# export_schema_json.py
import json
from utils.schema_io import load_schema

def schema_to_json(schema) -> dict:
    return {
        "extracted_at": str(schema.extracted_at),
        "tables": {
            table_name: {
                "schema": t.schema_name,
                "table": t.table_name,
                "columns": [
                    {
                        "name": col.column_name,
                        "type": col.data_type,
                        "nullable": col.is_nullable,
                        "default": col.column_default,
                        "is_primary_key": col.is_primary_key,
                        "is_foreign_key": col.is_foreign_key
                    }
                    for col in t.columns
                ],
                "foreign_keys": [
                    {
                        "column": fk.column_name,
                        "references": f"{fk.referenced_table_schema}.{fk.referenced_table_name}({fk.referenced_column_name})"
                    }
                    for fk in t.foreign_keys
                ]
            }
            for table_name, t in schema.tables.items()
        }
    }

def export_schema_to_json(pkl_path="metadata/database_schema.pkl", json_path="metadata/schema.json"):
    schema = load_schema(pkl_path)
    data = schema_to_json(schema)

    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Exported schema to {json_path}")

if __name__ == "__main__":
    export_schema_to_json()
