#!/usr/bin/env python3
"""
Debug script to check what data is stored for a user
"""

import requests
import json

def debug_user_data():
    print("🔍 Debugging User Data")
    print("=" * 30)
    
    user_id = "user_2xmGDBoXD6F0PdtaXUt1Us6skTz"
    
    # Check what documents exist for this user
    print(f"\n1. 📋 Checking documents for user: {user_id}")
    
    response = requests.get(f"http://localhost:3001/debug-docs/{user_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result.get('ids', []))} documents")
        
        ids = result.get('ids', [])
        metadatas = result.get('metadatas', [])
        documents = result.get('documents', [])
        
        for i, (doc_id, metadata, content) in enumerate(zip(ids, metadatas, documents)):
            print(f"\n   Document {i+1}:")
            print(f"   ID: {doc_id}")
            print(f"   Content: {content[:100]}...")
            print(f"   Metadata: {metadata}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test different queries with different thresholds
    print(f"\n2. 🧪 Testing different queries and thresholds")
    
    test_queries = [
        "what is eoxs",
        "steel erp company", 
        "rajat jain",
        "EOXS company"
    ]
    
    thresholds = [0.8, 0.6, 0.4]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        for threshold in thresholds:
            response = requests.post(
                f"http://localhost:3001/rag-context?similarity_threshold={threshold}",
                json={"userId": user_id, "query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     Threshold {threshold}: {result['relevantCount']}/{result['totalFound']} relevant")
                if result['context']:
                    print(f"     Context: {result['context'][:80]}...")
            else:
                print(f"     Threshold {threshold}: Error {response.status_code}")

if __name__ == "__main__":
    debug_user_data() 