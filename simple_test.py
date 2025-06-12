import requests
import json

def test_rag_generate():
    print("Testing RAG generate endpoint...")
    
    # First, store a user message
    user_msg = {
        "userId": "test_user",
        "messageId": "msg_1",
        "content": "I'm working on an IoT project for smart home automation",
        "metadata": {"project": "iot"}
    }
    
    response = requests.post("http://localhost:3001/embed", json=user_msg)
    print(f"Embed response: {response.status_code}")
    
    # Now test RAG generate
    query = {
        "userId": "test_user",
        "query": "What should I consider for my IoT project?"
    }
    
    response = requests.post("http://localhost:3001/rag-generate", json=query)
    print(f"RAG generate response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result.get('answer', 'No answer')[:100]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_rag_generate() 