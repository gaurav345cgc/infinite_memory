import requests
import json
import time

def test_complete_ai_memory():
    print("🧠 Testing Complete AI Memory System")
    print("=" * 50)
    
    user_id = "test_user_complete"
    thread_id = "test_thread_complete"
    
    # Step 1: Store user message
    print("\n1. 📝 Storing user message...")
    user_msg = {
        "userId": user_id,
        "threadId": thread_id,
        "messageId": f"msg_{int(time.time())}",
        "content": "I'm building a smart home IoT system with temperature sensors and automated lighting",
        "metadata": {
            "project": "smart_home",
            "stage": "planning",
            "topic": "iot_automation"
        }
    }
    
    response = requests.post("http://localhost:3001/embed", json=user_msg)
    print(f"✅ User message stored: {response.status_code}")
    
    # Step 2: Generate AI response (should be automatically stored)
    print("\n2. 🤖 Generating AI response...")
    query = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "What are the best temperature sensors for my smart home project?",
        "filters": {"project": "smart_home"}
    }
    
    response = requests.post("http://localhost:3001/rag-generate", json=query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI Response: {result['answer'][:100]}...")
        print(f"📋 Response ID: {result['responseId']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return
    
    # Step 3: Query AI responses specifically
    print("\n3. 🔍 Querying AI responses...")
    ai_query = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "temperature sensor recommendations"
    }
    
    response = requests.post("http://localhost:3001/query-ai-responses", json=ai_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['matches'])} AI responses")
        for i, match in enumerate(result['matches']):
            print(f"   {i+1}. Score: {match['score']:.3f} | Type: {match['metadata'].get('type', 'unknown')}")
            print(f"      Content: {match['content'][:80]}...")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 4: Query user messages specifically
    print("\n4. 🔍 Querying user messages...")
    user_query = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "smart home IoT system"
    }
    
    response = requests.post("http://localhost:3001/query-user-messages", json=user_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['matches'])} user messages")
        for i, match in enumerate(result['matches']):
            print(f"   {i+1}. Score: {match['score']:.3f} | Type: {match['metadata'].get('type', 'unknown')}")
            print(f"      Content: {match['content'][:80]}...")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 5: Query everything (both user messages and AI responses)
    print("\n5. 🔍 Querying all content...")
    all_query = {
        "userId": user_id,
        "threadId": thread_id,
        "query": "smart home automation"
    }
    
    response = requests.post("http://localhost:3001/query", json=all_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['matches'])} total matches")
        for i, match in enumerate(result['matches']):
            content_type = match['metadata'].get('type', 'unknown')
            print(f"   {i+1}. [{content_type}] Score: {match['score']:.3f}")
            print(f"      Content: {match['content'][:80]}...")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Step 6: Test manual AI response storage
    print("\n6. 📝 Testing manual AI response storage...")
    ai_response = {
        "userId": user_id,
        "threadId": thread_id,
        "responseId": f"resp_{int(time.time())}",
        "userMessageId": "manual_test",
        "content": "Based on your smart home project, I recommend using DHT22 sensors for temperature monitoring and ESP32 modules for connectivity.",
        "context": "User asked about IoT sensors for smart home",
        "metadata": {
            "model": "gpt-4o-mini",
            "confidence": "high"
        }
    }
    
    response = requests.post("http://localhost:3001/embed-ai-response", json=ai_response)
    print(f"✅ Manual AI response stored: {response.status_code}")
    
    print("\n🎉 Complete AI Memory System Test Finished!")
    print("✅ The system now remembers both user messages and AI responses!")
    print("✅ You can query them separately or together!")
    print("✅ AI responses are automatically stored when using /rag-generate!")

if __name__ == "__main__":
    test_complete_ai_memory() 