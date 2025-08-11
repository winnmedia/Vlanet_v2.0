#!/usr/bin/env python3
"""
Rate Limiting   
  Rate Limiting   .
"""

# .env   

def show_development_settings():
    """   """
    print("===   (.env.dev)   ===")
    
    env_content = """
#   
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings_dev

# Rate Limiting  
RATE_LIMITING_ENABLED=False

#   ()
RATE_LIMIT_WHITELIST_IPS=127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12

#   
RATE_LIMIT_TEST_ACCOUNTS=test@example.com,dev@vlanet.net,admin@vlanet.net,developer@example.com
"""
    print(env_content)

def show_staging_settings():
    """   """
    print("===   (.env.staging)   ===")
    
    env_content = """
#   
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings

# Rate Limiting   
RATE_LIMITING_ENABLED=True

#   (QA IP )
RATE_LIMIT_WHITELIST_IPS=127.0.0.1,::1,203.0.113.0/24

#   
RATE_LIMIT_TEST_ACCOUNTS=qa@vlanet.net,staging@example.com
"""
    print(env_content)

def show_production_settings():
    """   """
    print("===   (.env.production)   ===")
    
    env_content = """
#   
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings

# Rate Limiting  
RATE_LIMITING_ENABLED=True

#   (  IP)
RATE_LIMIT_WHITELIST_IPS=203.0.113.100,203.0.113.101

#    ()
RATE_LIMIT_TEST_ACCOUNTS=admin@vlanet.net
"""
    print(env_content)

def show_railway_settings():
    """Railway    """
    print("=== Railway    ===")
    
    railway_vars = {
        'DEBUG': 'False',
        'DJANGO_SETTINGS_MODULE': 'config.settings.railway',
        'RATE_LIMITING_ENABLED': 'True',
        'RATE_LIMIT_WHITELIST_IPS': '127.0.0.1,::1',
        'RATE_LIMIT_TEST_ACCOUNTS': '',
        'SECRET_KEY': 'your-production-secret-key',
        'DATABASE_URL': 'postgresql://user:pass@host:port/db',
    }
    
    print("Railway   :")
    for key, value in railway_vars.items():
        print(f"{key}={value}")

def show_runtime_control_examples():
    """  """
    print("\n===  Rate Limiting   ===")
    
    print("1.    Rate Limiting  :")
    print("   Railway : RATE_LIMITING_ENABLED=False")
    print("      ")
    
    print("\n2.  IP   :")
    print("   : RATE_LIMIT_WHITELIST_IPS=127.0.0.1,::1")
    print("   : RATE_LIMIT_WHITELIST_IPS=127.0.0.1,::1,203.0.113.50")
    
    print("\n3.     :")
    print("        ")
    
    print("\n4.    :")
    print("   RATE_LIMIT_TEST_ACCOUNTS=dev1@vlanet.net,dev2@vlanet.net,qa@vlanet.net")

def show_monitoring_tips():
    """ """
    print("\n=== Rate Limiting   ===")
    
    print("1.  :")
    print("   - Django  429   ")
    print("   - security.log   ")
    
    print("\n2.  :")
    print("   - Rate limit ")
    print("   -  IP ")
    print("   -   ")
    
    print("\n3.  :")
    print("   -  Rate limit   ")
    print("   -  IP    ")

def main():
    """  """
    print("Rate Limiting   \n")
    
    show_development_settings()
    print("\n" + "="*60 + "\n")
    
    show_staging_settings()
    print("\n" + "="*60 + "\n")
    
    show_production_settings()
    print("\n" + "="*60 + "\n")
    
    show_railway_settings()
    print("\n" + "="*60 + "\n")
    
    show_runtime_control_examples()
    print("\n" + "="*60 + "\n")
    
    show_monitoring_tips()
    
    print("\n" + "="*60)
    print(" :")
    print("1.      ")
    print("2. Railway     ")
    print("3.   RATE_LIMITING_ENABLED=False ")
    print("4.       ")

if __name__ == '__main__':
    main()