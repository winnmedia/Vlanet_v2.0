"""
  
Gmail App Password  
"""

import os
from django.core.exceptions import ImproperlyConfigured

def configure_email_settings():
    """
       .
    SendGrid API  .
    """
    # SendGrid API   SendGrid 
    if os.environ.get('SENDGRID_API_KEY'):
        settings = {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'smtp.sendgrid.net',
            'EMAIL_PORT': 587,
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST_USER': 'apikey',
            'EMAIL_HOST_PASSWORD': os.environ.get('SENDGRID_API_KEY'),
            'DEFAULT_FROM_EMAIL': os.environ.get('DEFAULT_FROM_EMAIL', 'VideoPlanet <noreply@vlanet.net>')
        }
        print(" SendGrid   ")
    else:
        # SendGrid  Gmail 
        settings = {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': 587,
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST_USER': os.environ.get('EMAIL_HOST_USER', ''),
            'EMAIL_HOST_PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD', ''),
            'DEFAULT_FROM_EMAIL': os.environ.get('DEFAULT_FROM_EMAIL', 'VideoPlanet <noreply@vlanet.net>')
        }
    
    #       
    #     ,    
    if os.environ.get('DEBUG', 'False').lower() == 'true':
        if not settings['EMAIL_HOST_PASSWORD']:
            settings['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
            return settings
        #      
    
    #     
    if not settings['EMAIL_HOST_PASSWORD']:
        #     
        print("""
             !
        
        SendGrid  :
        1. SendGrid  : https://sendgrid.com
        2. API  :
           - Settings → API Keys → Create API Key
           - Full Access  
           -  API  
        
        3. Railway  :
           SENDGRID_API_KEY=SG.-api--
           DEFAULT_FROM_EMAIL=VideoPlanet <noreply@vlanet.net>
        
         Gmail    :
        1. Google   : https://myaccount.google.com/security
        2. 2  
        3.   :
           - https://myaccount.google.com/apppasswords
           -  : 
           -  :  (VideoPlanet)
           -  16  
        
        4. Railway  :
           EMAIL_HOST_USER=your-email@gmail.com
           EMAIL_HOST_PASSWORD=16-- ( )
           DEFAULT_FROM_EMAIL=VideoPlanet <your-email@gmail.com>
        
        :  Gmail   .    .
        """)
        
        #       
        settings['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
    
    return settings


#    
EMAIL_SETUP_GUIDE = """
#    

## SendGrid  ()

### 
-   
-    (, )
-     (  100/)
-     

###  

1. **SendGrid  **
   - https://sendgrid.com 
   -   

2. **API  **
   - Settings → API Keys → Create API Key
   - API Key Name: VideoPlanet
   - API Key Permissions: Full Access
   - Create & View 
   -  API   (  !)

3. **Railway  **
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
   DEFAULT_FROM_EMAIL=VideoPlanet <noreply@vlanet.net>
   ```

4. **  ()**
   - Settings → Sender Authentication
   - Single Sender Verification  Domain Authentication
   -    

## Gmail  ()

## 1. Gmail   

###  
- Google  2    .

###  

1. **2  **
   - https://myaccount.google.com/security 
   - "2 " 
   -   2  

2. **  **
   - https://myaccount.google.com/apppasswords 
   -  : ""
   -  : "" → "VideoPlanet" 
   - "" 
   - 16   ( )

## 2. Railway  

Railway    :

```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop (  )
DEFAULT_FROM_EMAIL=VideoPlanet <your-email@gmail.com>
```

## 3.   

```python
# Django shell 
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from VideoPlanet.',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

##  

### "Username and Password not accepted" 
-  Gmail      
- 2    

### "Please log in via your web browser" 
- Gmail  "    " 
- https://myaccount.google.com/lesssecureapps

###    
1.    
2. Gmail     
3.   587   
"""

def save_email_guide():
    """    """
    with open('/home/winnmedia/VideoPlanet/vridge_back/EMAIL_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(EMAIL_SETUP_GUIDE)
    print("   EMAIL_SETUP_GUIDE.md  .")

if __name__ == "__main__":
    save_email_guide()