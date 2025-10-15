#!/usr/bin/env python3
"""
Simple database connection test without embeddings
"""
import asyncio
import sys
import os

# Add the code/python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code', 'python'))

from core.retriever import get_vector_db_client

async def test_database_connection():
    print("=== TESTING DATABASE CONNECTION (NO EMBEDDINGS) ===")
    
    try:
        # Test 1: Get client
        print("1. Getting database client...")
        client = get_vector_db_client()
        print(f"   ✓ Client created: {type(client).__name__}")
        print(f"   ✓ Database type: {client.db_type}")
        
        if hasattr(client, 'collection_name'):
            print(f"   ✓ Collection name: {client.collection_name}")
        
        # Test 2: Check if we can search (even if no results)
        print("\n2. Testing search functionality...")
        search_results = await client.search("test", site="BlazorDocs", limit=1)
        print(f"   ✓ Search completed: {len(search_results) if search_results else 0} results")
        
        if search_results:
            print("   ✓ Found existing data!")
            first_result = search_results[0]
            print(f"   ✓ Sample result ID: {first_result.get('id', 'N/A')}")
            print(f"   ✓ Sample result site: {first_result.get('site', 'N/A')}")
        else:
            print("   ✓ No data found (expected if not yet ingested)")
        
        print("\n✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during database test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
