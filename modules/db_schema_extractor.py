# modules/db_schema_extractor.py

import psycopg2
from config.db_config import DB_CONFIG


def extract_schema():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        SELECT 
            table_schema,
            table_name,
            column_name,
            data_type
        FROM 
            information_schema.columns
        WHERE 
            table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            table_schema, table_name, ordinal_position;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        schema_dict = {}
        for schema, table, column, dtype in rows:
            full_table = f"{schema}.{table}"
            if full_table not in schema_dict:
                schema_dict[full_table] = []
            schema_dict[full_table].append({
                "column_name": column,
                "data_type": dtype
            })

        cursor.close()
        conn.close()
        return schema_dict

    except Exception as e:
        print("[ERROR] Failed to extract schema:", e)
        return {}
