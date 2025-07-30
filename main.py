
# from modules.embedding_preparation import EmbeddingPreparer

# if __name__ == "__main__":
#     base_dir = "data"
#     preparer = EmbeddingPreparer(base_dir)
#     preparer.run()


# main.py
from LLMs.generate_sql import call_gpt_generate_sql
from services.query_executor import execute_sql
from core.database import DatabaseConnection
from config.settings import settings

def main():
    db = DatabaseConnection(config=settings.database_config)
    print(" Ask questions about your database. Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("Ask your question: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("👋 Exiting. Goodbye!")
            break

        try:
            print(" Generating SQL...")
            sql = call_gpt_generate_sql(user_input, "data/llm_schema.json")
            print(" SQL Generated:")
            print(sql)

            print("\n Executing SQL on PostgreSQL...")
            results = execute_sql(sql, db)

            print(" Results:")
            for row in results:
                print(row)

        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main()
