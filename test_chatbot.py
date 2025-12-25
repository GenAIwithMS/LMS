#!/usr/bin/env python3
"""
Simple test script for the LMS Chatbot API
This demonstrates how to call the chatbot API endpoint
"""

import requests
import json

# Replace with your actual JWT token
JWT_TOKEN = "your_jwt_token_here"

def test_chat_api(message, role="student"):
    """Test the chat API with a message"""

    url = "http://localhost:5000/api/chat"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JWT_TOKEN}"
    }

    data = {
        "message": message
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Assistant: {result['message']}")
            print(f"Role: {result['role']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    print("LMS Chatbot API Test")
    print("====================")

    # Example messages for different roles
    test_messages = [
        "Show me all students",
        "Create an announcement for my class",
        "Submit my assignment",
        "What assignments do I have?"
    ]

    for message in test_messages:
        print(f"\n👤 User: {message}")
        test_chat_api(message)
        print("-" * 50)