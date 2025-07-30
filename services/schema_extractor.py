# services/schema_extractor.py
from core.models import TableInfo, ColumnInfo, ForeignKeyInfo, IndexInfo,CheckConstraintInfo, DatabaseSchema
from core.database import DatabaseConnection
from typing import Dict, Optional, List


class SchemaExtractor:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def extract_schema(self, schemas: Optional[List[str]] = None) -> DatabaseSchema:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            params = []

            schema_filter = ""
            if schemas:
                schema_filter = " AND t.table_schema = ANY(%s)"
                params.append(schemas)

            # --- Fetch basic column info
            cursor.execute(f"""
                SELECT 
                    t.table_schema,
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable = 'YES' AS is_nullable,
                    c.column_default,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale
                FROM information_schema.tables t
                JOIN information_schema.columns c 
                    ON t.table_schema = c.table_schema 
                    AND t.table_name = c.table_name
                WHERE t.table_type = 'BASE TABLE'
                  AND t.table_schema NOT IN ('information_schema', 'pg_catalog')
                  {schema_filter}
            """, params)

            tables: Dict[str, TableInfo] = {}
            for row in cursor.fetchall():
                key = f"{row['table_schema']}.{row['table_name']}"
                if key not in tables:
                    tables[key] = TableInfo(
                        schema_name=row['table_schema'],
                        table_name=row['table_name'],
                        columns=[],
                        foreign_keys=[],
                        indexes=[],
                        check_constraints=[]
                    )
                tables[key].columns.append(ColumnInfo(
                    column_name=row['column_name'],
                    data_type=row['data_type'],
                    is_nullable=row['is_nullable'],
                    column_default=row['column_default'],
                    character_maximum_length=row['character_maximum_length'],
                    numeric_precision=row['numeric_precision'],
                    numeric_scale=row['numeric_scale']
                ))

            # --- Primary Keys
            cursor.execute("""
                SELECT
                    kc.table_schema,
                    kc.table_name,
                    kc.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kc
                  ON kc.constraint_name = tc.constraint_name
                 AND kc.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
            """)
            for row in cursor.fetchall():
                key = f"{row['table_schema']}.{row['table_name']}"
                table = tables.get(key)
                if table:
                    for col in table.columns:
                        if col.column_name == row['column_name']:
                            col.is_primary_key = True

            # --- Foreign Keys
            cursor.execute("""
                SELECT
                    con.conname AS constraint_name,
                    sch1.nspname AS table_schema,
                    rel1.relname AS table_name,
                    att1.attname AS column_name,
                    sch2.nspname AS foreign_table_schema,
                    rel2.relname AS foreign_table_name,
                    att2.attname AS foreign_column_name
                FROM pg_constraint con
                JOIN pg_class rel1 ON rel1.oid = con.conrelid
                JOIN pg_namespace sch1 ON sch1.oid = rel1.relnamespace
                JOIN pg_attribute att1 ON att1.attrelid = rel1.oid AND att1.attnum = ANY(con.conkey)
                JOIN pg_class rel2 ON rel2.oid = con.confrelid
                JOIN pg_namespace sch2 ON sch2.oid = rel2.relnamespace
                JOIN pg_attribute att2 ON att2.attrelid = rel2.oid AND att2.attnum = ANY(con.confkey)
                WHERE con.contype = 'f';
            """)
            for row in cursor.fetchall():
                key = f"{row['table_schema']}.{row['table_name']}"
                table = tables.get(key)
                if table:
                    table.foreign_keys.append(ForeignKeyInfo(
                        constraint_name=row['constraint_name'],
                        column_name=row['column_name'],
                        referenced_table_schema=row['foreign_table_schema'],
                        referenced_table_name=row['foreign_table_name'],
                        referenced_column_name=row['foreign_column_name']
                    ))
                    for col in table.columns:
                        if col.column_name == row['column_name']:
                            col.is_foreign_key = True
                            col.foreign_key_info = table.foreign_keys[-1]

            return DatabaseSchema(tables=tables)
