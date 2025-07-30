# modules/embedding_preparation.py

import json
from pathlib import Path

class EmbeddingPreparer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.schema_path = self.base_dir / 'llm_schema.json'
        self.chunk_txt_path = self.base_dir / 'embedding_chunks.txt'
        self.chunk_jsonl_path = self.base_dir / 'embedding_chunks.jsonl'
        self.metadata_path = self.base_dir / 'embedding_metadata.json'

    def load_schema(self):
        with open(self.schema_path, 'r') as f:
            return json.load(f)

    def clean_chunk(self, schema_name, table_name, columns, synonyms):
        """
        Convert table info to a plain text string for embedding.
        """
        text = f"Schema: {schema_name}\nTable: {table_name}\nColumns: {', '.join(columns)}"
        if synonyms:
            text += f"\nSynonyms: {', '.join(synonyms)}"
        return text.strip()

    def extract_chunks_and_metadata(self, schema_data):
        chunks = []
        metadata = []

        idx = 0
        for schema_name, schema in schema_data.get("schemas", {}).items():
            for table_name, table_info in schema.get("tables", {}).items():
                columns = [col["name"] for col in table_info.get("columns", [])]
                synonyms = table_info.get("synonyms", [])

                chunk_text = self.clean_chunk(schema_name, table_name, columns, synonyms)
                chunks.append(chunk_text)

                metadata.append({
                    "id": f"{schema_name}.{table_name}",
                    "schema": schema_name,
                    "table": table_name,
                    "columns": columns,
                    "synonyms": synonyms,
                    "ner_labels": [],
                    "embedding_index": idx
                })
                idx += 1

        return chunks, metadata

    def save_chunks_text(self, chunks):
        with open(self.chunk_txt_path, 'w') as f:
            for chunk in chunks:
                f.write(chunk + "\n")

    def save_chunks_jsonl(self, chunks):
        with open(self.chunk_jsonl_path, 'w') as f:
            for idx, chunk in enumerate(chunks):
                json.dump({"id": idx, "text": chunk}, f)
                f.write("\n")

    def save_metadata(self, metadata):
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def run(self):
        print("[*] Loading schema...")
        schema = self.load_schema()

        print("[*] Extracting chunks and metadata...")
        chunks, metadata = self.extract_chunks_and_metadata(schema)

        print("[*] Saving outputs...")
        self.save_chunks_text(chunks)
        self.save_chunks_jsonl(chunks)
        self.save_metadata(metadata)

        print(f"[✓] Prepared {len(chunks)} chunks and metadata.")
