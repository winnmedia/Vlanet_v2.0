#!/usr/bin/env python3
import requests
import json

#  
login_data = {
    "email": "ceo@winnmedia.co.kr",
    "password": "Qwerasdf!234"
}

#   API 
print("=" * 50)
print("  API ")
print("=" * 50)

# 1.   
url = "http://localhost:8000/api/auth/login/"
print(f"\n1.  : {url}")
print(f"   : {login_data}")

try:
    response = requests.post(url, json=login_data)
    print(f"    : {response.status_code}")
    print(f"   : {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        
        if access_token:
            print("\n  !")
            print(f"   Access Token: {access_token[:50]}...")
            
            #   
            print("\n2.   ")
            verify_url = "http://localhost:8000/api/auth/verify/"
            verify_response = requests.post(verify_url, json={"token": access_token})
            print(f"    : {verify_response.status_code}")
            print(f"   : {json.dumps(verify_response.json(), indent=2, ensure_ascii=False)}")
            
            #   
            print("\n3.    (/api/projects/)")
            headers = {"Authorization": f"Bearer {access_token}"}
            projects_response = requests.get("http://localhost:8000/api/projects/", headers=headers)
            print(f"    : {projects_response.status_code}")
            if projects_response.status_code == 200:
                print("      -    ")
            else:
                print(f"     : {projects_response.text}")
                
except Exception as e:
    print(f"  : {e}")

#    
print("\n" + "=" * 50)
print("  API ")
print("=" * 50)

old_url = "http://localhost:8000/users/login/"
print(f"\n : {old_url}")
try:
    old_response = requests.post(old_url, json=login_data)
    print(f" : {old_response.status_code}")
    if old_response.status_code == 200:
        print(" :", list(old_response.json().keys()))
except Exception as e:
    print(f": {e}")