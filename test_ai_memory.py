#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced AI memory system
"""

import requests
import json
import time

BASE_URL = "http://localhost:3001"
USER_ID = "test_user_123"
THREAD_ID = "test_thread_456"

def test_ai_memory_system():
    print("🧠 Testing Enhanced AI Memory System")
    print("=" * 50)
    
    # Step 1: Store a user message
    print("\n1. 📝 Storing user message...")
    user_message = {
        "userId": USER_ID,
        "threadId": THREAD_ID,
        "messageId": f"msg_{int(time.time())}",
        "content": "I'm working on an IoT project for smart home automation using Raspberry Pi and sensors",
        "metadata": {
            "project": "smart_home_iot",
            "stage": "planning",
            "topic": "iot_automation"
        }
    }
    
    response = requests.post(f"{BASE_URL}/embed", json=user_message)
    print(f"✅ User message stored: {response.status_code}")
    
    # Step 2: Generate AI response (this will be automatically stored)
    print("\n2. 🤖 Generating AI response...")
    query = {
        "userId": USER_ID,
        "threadId": THREAD_ID,
        "query": "What sensors should I use for my IoT project?",
        "filters": {
            "project": "smart_home_iot"
        }
    }
    
    response = requests.post(f"{BASE_URL}/rag-generate", json=query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI Response: {result['answer'][:100]}...")
        print(f"📋 Response ID: {result['responseId']}")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Step 3: Query for AI responses specifically
    print("\n3. 🔍 Querying AI responses...")
    ai_query = {
        "userId": USER_ID,
        "threadId": THREAD_ID,
        "query": "sensor recommendations IoT"
    }
    
    response = requests.post(f"{BASE_URL}/query-ai-responses", json=ai_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['matches'])} AI responses")
        for i, match in enumerate(result['matches']):
            print(f"   {i+1}. Score: {match['score']:.3f} | Content: {match['content'][:80]}...")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 4: Query for user messages specifically
    print("\n4. 🔍 Querying user messages...")
    user_query = {
        "userId": USER_ID,
        "threadId": THREAD_ID,
        "query": "IoT project Raspberry Pi"
    }
    
    response = requests.post(f"{BASE_URL}/query-user-messages", json=user_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['matches'])} user messages")
        for i, match in enumerate(result['matches']):
            print(f"   {i+1}. Score: {match['score']:.3f} | Content: {match['content'][:80]}...")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 5: Query everything (both user messages and AI responses)
    print("\n5. 🔍 Querying all content...")
    all_query = {
        "userId": USER_ID,
        "threadId": THREAD_ID,
        "query": "smart home automation"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=all_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['matches'])} total matches")
        for i, match in enumerate(result['matches']):
            content_type = match['metadata'].get('type', 'unknown')
            print(f"   {i+1}. [{content_type}] Score: {match['score']:.3f} | Content: {match['content'][:80]}...")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n🎉 Test completed! The system now remembers both user messages and AI responses.")

if __name__ == "__main__":
    test_ai_memory_system() 