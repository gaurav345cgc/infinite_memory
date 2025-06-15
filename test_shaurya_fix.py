#!/usr/bin/env python3
"""
Test script to verify the Shaurya RAG fix
"""

import requests
import json
import time

def test_shaurya_fix():
    print("🔍 Testing Shaurya RAG Fix")
    print("=" * 30)
    
    user_id = "user_2xdTnz6ZkFCbDxHWRMOzVY3XP6K"
    
    # Test the RAG generate endpoint
    print("\n1. 🤖 Testing RAG generate for 'who is shaurya'...")
    query = {
        "userId": user_id,
        "query": "who is shaurya"
    }
    
    try:
        response = requests.post("http://localhost:3001/rag-generate", json=query, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Answer: {result.get('answer', 'No answer')}")
            print(f"📋 Full Context: {result.get('context', 'No context')}")
            print(f"🆔 Response ID: {result.get('responseId', 'No ID')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test the RAG context endpoint
    print("\n2. 🔍 Testing RAG context for 'who is shaurya'...")
    try:
        response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.3", json=query, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Context: {result.get('context', 'No context')}")
            print(f"📊 Relevant Count: {result.get('relevantCount', 0)}")
            print(f"📊 Total Found: {result.get('totalFound', 0)}")
            print(f"📊 Similarity Scores: {result.get('similarityScores', [])}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_shaurya_fix() 