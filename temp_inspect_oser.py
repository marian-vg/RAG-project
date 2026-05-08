import json
import os

# Load config
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)

chroma_path = config_data["chroma_path"]
collection_name = config_data["collection_name"]

print(f"[*] Chroma path: {chroma_path}")
print(f"[*] Collection: {collection_name}")

import chromadb

# Connect to Chroma
client = chromadb.PersistentClient(path=chroma_path)
collection = client.get_collection(name=collection_name)

# Get ALL documents with metadata
all_data = collection.get(include=["documents", "metadatas"])

print(f"[*] Total chunks in collection: {len(all_data['ids'])}")
print(f"[*] Searching for OSER chunks...")
print("=" * 80)

oser_count = 0
for i, (doc_id, document, metadata) in enumerate(zip(all_data['ids'], all_data['documents'], all_data['metadatas'])):
    entidad = metadata.get('entidad', '') if metadata else ''
    if entidad == 'OSER':
        oser_count += 1
        source = metadata.get('source', 'unknown') if metadata else 'unknown'
        page_number = metadata.get('page_number', 'unknown') if metadata else 'unknown'
        print(f"\n[OSER Chunk #{oser_count}] ID: {doc_id}")
        print(f"  Source: {source}")
        print(f"  Page: {page_number}")
        print(f"  Content:\n{document}")
        print("-" * 80)

print(f"\n[*] Total OSER chunks found: {oser_count}")
