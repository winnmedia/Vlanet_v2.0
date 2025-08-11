#!/usr/bin/env python3
import requests
import json

# 
login_response = requests.post('http://localhost:8000/api/users/login/', 
    json={
        'email': 'ceo@winnmedia.co.kr',
        'password': 'Qwerasdf!234'
    },
    headers={'Content-Type': 'application/json'}
)

if login_response.status_code == 200:
    token = login_response.json().get('vridge_session')
    print(f" ! : {token[:20]}...")
    
    # PDF   
    planning_data = {
        'title': 'VideoPlanet  ',
        'project_type': 'promotional',
        'duration': '3',
        'target_audience': '  ',
        'genre': '/',
        'concept': '   ',
        'tone_manner': '  ',
        'key_message': 'AI    10 ',
        'desired_mood': ' ',
        'planning_text': 'VideoPlanet AI        .   3-5    5    .',
        'stories': [
            {
                'phase': '',
                'content': '   -       ',
                'key_point': ' '
            },
            {
                'phase': '',
                'content': 'VideoPlanet  - AI   ',
                'key_point': ' '
            },
            {
                'phase': '',
                'content': '   -     90% ',
                'key_point': ' '
            },
            {
                'phase': '',
                'content': '   -    ',
                'key_point': 'CTA'
            }
        ],
        'scenes': [
            {
                'title': ' ',
                'description': '     ',
                'location': '',
                'storyboards': []
            },
            {
                'title': 'VideoPlanet ',
                'description': 'AI    ',
                'location': ' ',
                'storyboards': []
            }
        ],
        'planning_options': {
            'colorTone': 'cinematic',
            'aspectRatio': '16:9',
            'cameraType': 'cinema',
            'lensType': '35mm',
            'cameraMovement': 'dolly'
        }
    }
    
    # PDF  
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    pdf_response = requests.post(
        'http://localhost:8000/api/video-planning/export/pdf/',
        headers=headers,
        json={
            'planning_data': planning_data,
            'use_enhanced_layout': True
        }
    )
    
    print(f"PDF  : {pdf_response.status_code}")
    
    if pdf_response.status_code == 200:
        # PDF  
        with open('test_export.pdf', 'wb') as f:
            f.write(pdf_response.content)
        print("PDF  test_export.pdf .")
    else:
        print(f": {pdf_response.text}")
else:
    print(f" : {login_response.text}")