#!/usr/bin/env python3
"""
Debug script to check similarity scores
"""

import requests
import json
import time

def debug_similarity_scores():
    print("🔍 Debugging Similarity Scores")
    print("=" * 35)
    
    user_id = "test_user_filter"
    thread_id = "test_thread_filter"
    
    # Test query
    query_google = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "what is google"
    }
    
    # Test with very low threshold to see all scores
    print("\n1. 🔍 Testing with very low threshold (0.0) to see all scores...")
    response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.0", json=query_google)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context: {result['context'][:200]}..." if result['context'] else "✅ Context: Empty")
        print(f"📊 Relevant Count: {result['relevantCount']}")
        print(f"📊 Total Found: {result['totalFound']}")
        print(f"📊 Threshold: {result['threshold']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test with medium threshold
    print("\n2. 🔍 Testing with medium threshold (0.5)...")
    response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.5", json=query_google)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context: {result['context'][:200]}..." if result['context'] else "✅ Context: Empty")
        print(f"📊 Relevant Count: {result['relevantCount']}")
        print(f"📊 Total Found: {result['totalFound']}")
        print(f"📊 Threshold: {result['threshold']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test with high threshold
    print("\n3. 🔍 Testing with high threshold (0.8)...")
    response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.8", json=query_google)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context: {result['context'][:200]}..." if result['context'] else "✅ Context: Empty")
        print(f"📊 Relevant Count: {result['relevantCount']}")
        print(f"📊 Total Found: {result['totalFound']}")
        print(f"📊 Threshold: {result['threshold']}")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    debug_similarity_scores() 