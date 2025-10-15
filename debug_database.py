#!/usr/bin/env python3
"""
Debug script to test database connection and upload
"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the code/python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code', 'python'))

from core.retriever import get_vector_db_client, upload_documents
from core.embedding import batch_get_embeddings
from core.config import CONFIG

async def test_database():
    print("=== TESTING DATABASE CONNECTION ===")
    
    # Check if OpenAI API key is loaded
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print(f"✓ OpenAI API key loaded: {openai_key[:20]}...")
    else:
        print("❌ OpenAI API key not found in environment!")
        return

    try:
        # Test 1: Get client
        print("1. Getting database client...")
        client = get_vector_db_client()
        print(f"   ✓ Client created: {type(client).__name__}")
        print(f"   ✓ Database type: {client.db_type}")

        if hasattr(client, 'collection_name'):
            print(f"   ✓ Collection name: {client.collection_name}")

        # Test 2: Create a simple test document
        print("\n2. Creating test document...")
        test_doc = {
            "id": "test-doc-123",
            "url": "https://test.example.com",
            "name": "Test Document",
            "site": "BlazorDocs",
            "text": "This is a test document for Blazor UI components.",
            "headline": "Test Headline",
            "description": "Test description",
            "tags": ["test", "blazor"],
            "schema_json": json.dumps({"test": "data"})
        }
        print(f"   ✓ Test document created with keys: {list(test_doc.keys())}")

        # Test 3: Generate embedding
        print("\n3. Generating embedding...")
        provider = CONFIG.preferred_embedding_provider
        provider_config = CONFIG.get_embedding_provider(provider)
        model = provider_config.model if provider_config else None

        print(f"   ✓ Embedding provider: {provider}")
        print(f"   ✓ Model: {model}")

        embeddings = await batch_get_embeddings([test_doc["text"]], provider, model)
        print(f"   ✓ Embedding generated: length {len(embeddings[0]) if embeddings else 0}")

        # Add embedding to document
        test_doc["embedding"] = embeddings[0]

        # Test 4: Upload document
        print("\n4. Uploading document...")
        result = await upload_documents([test_doc])
        print(f"   ✓ Upload result: {result}")

        # Test 5: Search for the document
        print("\n5. Searching for uploaded document...")
        search_results = await client.search("Blazor", site="BlazorDocs", limit=5)
        print(f"   ✓ Search returned: {len(search_results) if search_results else 0} results")

        if search_results:
            first_result = search_results[0]
            print(f"   ✓ First result ID: {first_result.get('id', 'N/A')}")
            print(f"   ✓ First result site: {first_result.get('site', 'N/A')}")
            print(f"   ✓ First result text preview: {str(first_result.get('text', 'N/A'))[:100]}...")

        print("\n✅ Database connection test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during database test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())
