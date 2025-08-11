#!/usr/bin/env python3
import requests
import json

#  
url = "http://localhost:8000/api/users/login/"
data = {
    "email": "ceo@winnmedia.co.kr",
    "password": "Qwerasdf!234"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n !")
        response_data = response.json()
        if 'access' in response_data:
            print(f"Access Token: {response_data['access'][:50]}...")
    else:
        print("\n !")
        
except Exception as e:
    print(f" : {e}")