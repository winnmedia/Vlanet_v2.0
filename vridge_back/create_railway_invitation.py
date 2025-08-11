#!/usr/bin/env python3
"""
Railway     
"""
import requests
import json

def create_invitation_via_api():
    """API   """
    print("=== Railway API    ===")
    
    #  API  ( )
    login_url = "https://videoplanet.up.railway.app/api/users/login/"
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        #  
        session = requests.Session()
        
        print("  ...")
        login_response = session.post(login_url, json=login_data)
        print(f"  : {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"  : {login_response.text}")
            return
        
        login_result = login_response.json()
        print(f"  : {login_result.get('message')}")
        
        #   
        print("\n   ...")
        projects_url = "https://videoplanet.up.railway.app/api/projects/"
        projects_response = session.get(projects_url)
        print(f"   : {projects_response.status_code}")
        
        if projects_response.status_code != 200:
            print(f"    : {projects_response.text}")
            return
        
        projects_data = projects_response.json()
        projects = projects_data.get('projects', [])
        
        if not projects:
            print("  .   ...")
            
            #  
            create_url = "https://videoplanet.up.railway.app/api/projects/create/"
            create_data = {
                "name": " ",
                "manager": " ",
                "consumer": " ",
                "description": "API  ."
            }
            
            create_response = session.post(create_url, json=create_data)
            print(f"   : {create_response.status_code}")
            
            if create_response.status_code != 201:
                print(f"   : {create_response.text}")
                return
            
            project_result = create_response.json()
            project_id = project_result.get('project_id')
            print(f"   : ID {project_id}")
            
        else:
            project_id = projects[0]['id']
            print(f"   : ID {project_id}")
        
        #  
        print(f"\n   ... ( ID: {project_id})")
        invite_url = f"https://videoplanet.up.railway.app/api/projects/{project_id}/invitations/"
        invite_data = {
            "invitee_email": "invite_test@example.com",
            "message": "API  ."
        }
        
        invite_response = session.post(invite_url, json=invite_data)
        print(f"   : {invite_response.status_code}")
        
        if invite_response.status_code not in [200, 201]:
            print(f"   : {invite_response.text}")
            return
        
        invite_result = invite_response.json()
        invitation_id = invite_result.get('invitation_id')
        print(f"   : ID {invitation_id}")
        
        #    
        print(f"\n    ...")
        invitations_url = f"https://videoplanet.up.railway.app/api/projects/{project_id}/invitations/"
        invitations_response = session.get(invitations_url)
        
        if invitations_response.status_code == 200:
            invitations_data = invitations_response.json()
            invitations = invitations_data.get('invitations', [])
            
            if invitations:
                invitation = invitations[0]  #   
                token = invitation.get('token')
                
                print(f"  :")
                print(f"- ID: {invitation.get('id')}")
                print(f"- : {token}")
                print(f"- : {invitation.get('status')}")
                print(f"-  : {invitation.get('invitee_email')}")
                print(f"- : {invitation.get('expires_at')}")
                
                #   API 
                if token:
                    print(f"\n   API ...")
                    token_url = f"https://videoplanet.up.railway.app/api/projects/invitations/token/{token}/"
                    token_response = requests.get(token_url)  #  
                    print(f"   : {token_response.status_code}")
                    
                    if token_response.status_code == 200:
                        token_data = token_response.json()
                        print(f"   :")
                        print(f"- : {token_data.get('status')}")
                        if 'invitation' in token_data:
                            inv_data = token_data['invitation']
                            print(f"- : {inv_data.get('project', {}).get('name')}")
                            print(f"- : {inv_data.get('inviter', {}).get('nickname')}")
                        
                        #  URL 
                        frontend_url = f"https://vlanet.net/invitation/{token}"
                        print(f"\n  URL: {frontend_url}")
                        
                    else:
                        print(f"   : {token_response.text}")
                
            else:
                print("   .")
        else:
            print(f"    : {invitations_response.text}")
    
    except Exception as e:
        print(f"  : {str(e)}")

if __name__ == "__main__":
    create_invitation_via_api()