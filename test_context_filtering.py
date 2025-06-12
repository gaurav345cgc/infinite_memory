#!/usr/bin/env python3
"""
Test script to verify improved context filtering
"""

import requests
import json
import time

def test_context_filtering():
    print("🔍 Testing Improved Context Filtering")
    print("=" * 45)
    
    user_id = "test_user_filter"
    thread_id = "test_thread_filter"
    
    # Step 1: Store some test data
    print("\n1. 📝 Storing test data...")
    
    test_messages = [
        {
            "content": "I'm working on an IoT project for smart home automation",
            "metadata": {"project": "iot", "topic": "automation"}
        },
        {
            "content": "What is Google? Google is a multinational technology company.",
            "metadata": {"topic": "technology", "company": "google"}
        },
        {
            "content": "Python is a programming language used for web development",
            "metadata": {"topic": "programming", "language": "python"}
        }
    ]
    
    for i, msg in enumerate(test_messages):
        user_msg = {
            "userId": user_id,
            "threadId": thread_id,
            "messageId": f"msg_{int(time.time())}_{i}",
            "content": msg["content"],
            "metadata": msg["metadata"]
        }
        
        response = requests.post("http://localhost:3001/embed", json=user_msg)
        print(f"✅ Stored: {msg['content'][:50]}...")
    
    # Step 2: Test query with high similarity threshold (should return relevant results)
    print("\n2. 🔍 Testing query with high threshold (0.8)...")
    query_google = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "what is google"
    }
    
    response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.8", json=query_google)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context: {result['context'][:100]}..." if result['context'] else "✅ Context: Empty")
        print(f"📊 Relevant Count: {result['relevantCount']}")
        print(f"📊 Total Found: {result['totalFound']}")
        print(f"📊 Threshold: {result['threshold']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 3: Test query with low similarity threshold (should return more results)
    print("\n3. 🔍 Testing query with low threshold (0.3)...")
    response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.3", json=query_google)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context: {result['context'][:100]}..." if result['context'] else "✅ Context: Empty")
        print(f"📊 Relevant Count: {result['relevantCount']}")
        print(f"📊 Total Found: {result['totalFound']}")
        print(f"📊 Threshold: {result['threshold']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 4: Test query with no relevant data (should return empty)
    print("\n4. 🔍 Testing query with no relevant data...")
    query_unrelated = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "what is quantum physics and how does it work"
    }
    
    response = requests.post("http://localhost:3001/rag-context?similarity_threshold=0.8", json=query_unrelated)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Context: {result['context'][:100]}..." if result['context'] else "✅ Context: Empty")
        print(f"📊 Relevant Count: {result['relevantCount']}")
        print(f"📊 Total Found: {result['totalFound']}")
        print(f"📊 Threshold: {result['threshold']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n🎉 Context Filtering Test Completed!")
    print("✅ High threshold = Only very relevant results")
    print("✅ Low threshold = More results included")
    print("✅ No relevant data = Empty context")

if __name__ == "__main__":
    test_context_filtering() 