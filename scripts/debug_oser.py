"""Debug OSER document chunking."""
import sys
sys.path.insert(0, '.')

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import glob
import os

config_path = 'config.json'
import json
with open(config_path, 'r') as f:
    config = json.load(f)

os.makedirs('chroma_db', exist_ok=True)

# Load OSER document
oser_files = [f for f in glob.glob('documentos/*.pdf') if 'OSER' in f.upper()]
print(f'OSER files: {oser_files}')

for os_path in oser_files:
    print(f'\n=== Processing {os_path} ===')
    loader = UnstructuredPDFLoader(os_path, strategy='fast', mode='elements', languages=['spa'])
    elements = loader.load()
    print(f'Elements loaded: {len(elements)}')

    full_text = '\n'.join([el.page_content for el in elements])
    print(f'Total text length: {len(full_text)}')
    print(f'First 500 chars: {full_text[:500]}')

    # Show each element content
    for i, el in enumerate(elements[:5]):
        print(f'\nElement {i}: type={el.metadata.get("category", "?")} | content_len={len(el.page_content)}')
        print(f'Content: {el.page_content[:200]}...')