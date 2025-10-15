#!/usr/bin/env python3
"""
Debug script to test data ingestion
"""
import asyncio
import sys
import os

# Add the code/python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code', 'python'))

from data_loading.db_load_utils import prepare_documents_from_json

async def test_ingestion():
    print("=== TESTING DATA INGESTION ===")

    # Read the first line from the JSONL file
    jsonl_file = "progress-code/telerik-blazor-docs.jsonl"

    if not os.path.exists(jsonl_file):
        print(f"ERROR: File not found: {jsonl_file}")
        return

    with open(jsonl_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()

    print(f"First line length: {len(first_line)}")
    print(f"First line preview: {first_line[:200]}...")

    # Test the prepare_documents_from_json function
    try:
        import json
        json_obj = json.loads(first_line)
        url = json_obj.get('url', 'https://example.com/test')

        print(f"\nTesting with URL: {url}")
        print(f"JSON keys: {list(json_obj.keys())}")

        # Call the function
        documents, texts = prepare_documents_from_json(url, first_line, "BlazorDocs")

        print(f"\nResults:")
        print(f"Documents returned: {len(documents)}")
        print(f"Texts returned: {len(texts)}")

        if documents:
            print(f"\nFirst document structure:")
            first_doc = documents[0]
            for key, value in first_doc.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")

        if texts:
            print(f"\nFirst text for embedding:")
            print(f"Length: {len(texts[0])}")
            print(f"Preview: {texts[0][:200]}...")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ingestion())
