from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ForeignKeyInfo(BaseModel):
    """Model for foreign key constraint information."""

    constraint_name: str = Field(..., description="Foreign key constraint name")
    column_name: str = Field(..., description="Column that references foreign table")
    referenced_table_schema: str = Field(..., description="Referenced table schema")
    referenced_table_name: str = Field(..., description="Referenced table name")
    referenced_column_name: str = Field(..., description="Referenced column name")

    @property
    def referenced_table_full_name(self) -> str:
        """Get fully qualified referenced table name."""
        return f"{self.referenced_table_schema}.{self.referenced_table_name}"

class IndexInfo(BaseModel):
    """Model for index information."""

    index_name: str = Field(..., description="Index name")
    is_unique: bool = Field(default=False, description="Whether index is unique")
    is_primary: bool = Field(default=False, description="Whether index is primary key")
    columns: List[str] = Field(default_factory=list, description="Columns in the index")
    index_type: str = Field(default="btree", description="Index type (btree, hash, etc.)")

class CheckConstraintInfo(BaseModel):
    """Model for check constraint information."""

    constraint_name: str = Field(..., description="Check constraint name")
    check_clause: str = Field(..., description="Check constraint definition")

class ColumnInfo(BaseModel):
    """Model for database column information."""

    column_name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Column data type")
    is_nullable: bool = Field(default=True, description="Whether column accepts NULL values")
    column_default: Optional[str] = Field(None, description="Default value for column")
    character_maximum_length: Optional[int] = Field(None, description="Maximum character length")
    numeric_precision: Optional[int] = Field(None, description="Numeric precision")
    numeric_scale: Optional[int] = Field(None, description="Numeric scale")
    is_primary_key: bool = Field(default=False, description="Whether column is part of primary key")
    is_foreign_key: bool = Field(default=False, description="Whether column is a foreign key")
    foreign_key_info: Optional[ForeignKeyInfo] = Field(None, description="Foreign key details if applicable")

class TableInfo(BaseModel):
    """Model for database table information."""

    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")
    columns: List[ColumnInfo] = Field(default_factory=list, description="List of columns")
    foreign_keys: List[ForeignKeyInfo] = Field(default_factory=list, description="Foreign key constraints")
    indexes: List[IndexInfo] = Field(default_factory=list, description="Table indexes")
    check_constraints: List[CheckConstraintInfo] = Field(default_factory=list, description="Check constraints")
    
    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema_name}.{self.table_name}"
    
    @property
    def primary_key_columns(self) -> List[str]:
        """Get primary key column names."""
        return [col.column_name for col in self.columns if col.is_primary_key]
    
    @property
    def foreign_key_columns(self) -> List[str]:
        """Get foreign key column names."""
        return [col.column_name for col in self.columns if col.is_foreign_key]
    
    def get_foreign_key_for_column(self, column_name: str) -> Optional[ForeignKeyInfo]:
        """Get foreign key info for a specific column."""
        for fk in self.foreign_keys:
            if fk.column_name == column_name:
                return fk
        return None

class DatabaseSchema(BaseModel):
    """Model for complete database schema."""
    tables: Dict[str, TableInfo] = Field(default_factory=dict, description="Dictionary of tables")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    
    def get_table(self, schema_name: str, table_name: str) -> Optional[TableInfo]:
        """Get table by schema and table name."""
        full_name = f"{schema_name}.{table_name}"
        return self.tables.get(full_name)
    
    def get_tables_in_schema(self, schema_name: str) -> List[TableInfo]:
        """Get all tables in a specific schema."""
        return [
            table for table in self.tables.values()
            if table.schema_name == schema_name
        ]
    
    def get_relationships(self) -> List[Dict[str, str]]:
        """Get all foreign key relationships in the database."""
        relationships = []
        for table in self.tables.values():
            for fk in table.foreign_keys:
                relationships.append({
                    "from_table": table.full_name,
                    "from_column": fk.column_name,
                    "to_table": fk.referenced_table_full_name,
                    "to_column": fk.referenced_column_name,
                    "constraint_name": fk.constraint_name
                })
        return relationships
    
    def get_related_tables(self, table_full_name: str) -> Dict[str, List[str]]:
        """Get tables that reference this table and tables this table references."""
        
        references_to = []  # Tables this table references
        referenced_by = []  # Tables that reference this table
        
        for table in self.tables.values():
            for fk in table.foreign_keys:
                if fk.referenced_table_full_name == table_full_name:
                    referenced_by.append(table.full_name)
                elif table.full_name == table_full_name:
                    references_to.append(fk.referenced_table_full_name)
        
        return {
            "references_to": references_to,
            "referenced_by": referenced_by
        }