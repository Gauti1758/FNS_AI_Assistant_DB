from config.settings import settings
from core.database import DatabaseConnection
from services.schema_extractor import SchemaExtractor
from utils.schema_io import save_schema

from pprint import pprint

db = DatabaseConnection(settings.database_config)
extractor = SchemaExtractor(db)

schema = extractor.extract_schema()
pprint(schema.dict(), indent=2)
save_schema(schema, "metadata/database_schema.pkl")

print("✅ Schema extracted and saved.")