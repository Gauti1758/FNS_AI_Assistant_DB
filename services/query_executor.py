# services/query_executor.py
from core.database import DatabaseConnection

def execute_sql(sql: str, db: DatabaseConnection):
    with db.get_connection(use_real_dict_cursor=False) as conn:  
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in rows]
    return results
