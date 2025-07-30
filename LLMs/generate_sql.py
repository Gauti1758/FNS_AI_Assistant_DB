import os
import json
import requests

# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_KEY = "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"    #need to move it to env
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"  

def call_gpt_generate_sql(user_query: str, schema_json_path: str) -> str:
    with open(schema_json_path, "r") as f:
        schema = json.load(f)

    prompt = f"""
You are a PostgreSQL expert.
Given this database schema and a user question, generate an SQL query that best answers the user's intent.
Avoid DROP, DELETE, INSERT, or UPDATE unless explicitly asked. Only return valid SQL query in your response.Use only the schema provided to answer user's query. Do not include explanations.

Schema:
{json.dumps(schema, indent=2)}

User Query:
{user_query}

SQL Query:

Rules:
- Only use the above schema. Do not guess table or column names.
- Always use qualified names like ticket_schema.users.name
- If the question cannot be answered from the schema, say: "Sorry, I cannot answer that based on the available schema."
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()
    sql = result["choices"][0]["message"]["content"].strip()
    return sql
