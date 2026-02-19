import requests
import base64
import mail
import time
import os
import random
import string
import json

logo = f"""

 █████╗ ██████╗  █████╗ ███████╗ █████╗ ████████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████║██████╔╝███████║█████╗  ███████║   ██║
██╔══██║██╔══██╗██╔══██║██╔══╝  ██╔══██║   ██║
██║  ██║██║  ██║██║  ██║██║     ██║  ██║   ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝   ╚═╝
----------------------------------------------------
\033[1;34m------------------------------------------\033[0m"""

os.system('cls' if os.name == 'nt' else 'clear')
print(logo)
base_url = input('> Input base url (e.g., http://localhost:5000): ')
refcode = input('> Referral code: ')
print('\033[1;34m------------------------------------------\033[0m')

def generate_password(length=8):
    if length < 8:
        length = 8

    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("@#$&")

    remaining = ''.join(random.choices(string.ascii_letters + string.digits + "@#$&", k=length - 4))

    password = upper + lower + digit + special + remaining
    encoded_password = base64.b64encode(password.encode()).decode()
    return encoded_password

def get_proxy():
    try:
        with open('proxy.txt', 'r') as file:
            proxy_line = file.read().strip()
        
        if not proxy_line:
            print("No proxy found in proxy.txt")
            return None
            
        print(f"Raw proxy: {proxy_line}")
        
        clean_proxy = proxy_line.replace('http://', '').replace('https://', '')
        
        if '@' in clean_proxy:
            proxy_dict = {
                'http': f'http://{clean_proxy}',
                'https': f'http://{clean_proxy}'
            }
            print(f"Using proxy: {proxy_dict}")
            return proxy_dict
            
        parts = clean_proxy.split(':')
        if len(parts) == 4:
            user, password, host, port = parts
            correct_format = f"{user}:{password}@{host}:{port}"
            proxy_dict = {
                'http': f'http://{correct_format}',
                'https': f'http://{correct_format}'
            }
            print(f"Fixed proxy: {proxy_dict}")
            return proxy_dict
        else:
            print(f"Invalid proxy format. Use: user:pass@host:port")
            return None
            
    except Exception as e:
        print(f"Proxy error: {e}")
        return None

def create_account(captcha_token, password, email, proxy):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://m.sosovalue.com',
        'referer': 'https://m.sosovalue.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    json_data = {
        'email': email,
        'password': password,
        'rePassword': password,
        'username': email.split('@')[0],
    }
    
    params = {
        'cf-turnstile-response': captcha_token,
    }
    
    try:
        response = requests.post(
            'https://gw.sosovalue.com/usercenter/email/anno/sendRegisterVerifyCode/V2',
            params=params,
            headers=headers,
            json=json_data,
            proxies=proxy,
            timeout=30
        )
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return {'code': 999, 'message': str(e)}

def verify_email(password, email, code, refcode, proxy):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://m.sosovalue.com',
        'referer': 'https://m.sosovalue.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    json_data = {
        'password': password,
        'rePassword': password,
        'username': email.split('@')[0],
        'email': email,
        'verifyCode': code,
        'invitationCode': refcode,
    }
    
    try:
        response = requests.post(
            'https://gw.sosovalue.com/usercenter/user/anno/v3/register',
            headers=headers,
            json=json_data,
            proxies=proxy,
            timeout=30
        )
        return response.json()
    except Exception as e:
        print(f"Verify error: {e}")
        return {'code': 999, 'message': str(e)}

def get_captcha():
    global base_url
    while True:
        try:
            token = requests.get(f'{base_url}/get', timeout=10).text
            if token != "No tokens available":
                return token
            else:
                time.sleep(0.3)
        except Exception as e:
            print(f"Captcha error: {e}")
            time.sleep(1)

while True:
    try:
        email = mail.getmails()
        print('> \033[1;32mNew email :', email)
        
        password = generate_password()
        decpass = str(base64.b64decode(password.encode())).replace("b'", '').replace("'", '')
        print('\033[0m> \033[1;32mPassword :', decpass)
        
        captcha_token = get_captcha()
        print('> Captcha token obtained')
        
        proxy = get_proxy()
        print('> Testing without proxy first...')
        proxy = None  # Test without proxy first
        
        create_account_response = create_account(captcha_token, password, email, proxy)
        
        if create_account_response.get('code') == 0:
            print(f'>\033[1;32m Email sent successfully \033[0m')
            
            username, domain = email.split('@')
            print('> Waiting for verification code...')
            code = mail.get_verification_link(email, domain)
            
            if code:
                print(f'> Verification code: {code}')
                verify_response = verify_email(password, email, code, refcode, proxy)
                
                if verify_response.get('code') == 0:
                    with open('accounts.txt', 'a') as file:
                        file.write(f"Email: {email}\n")
                        file.write(f"Password: {decpass}\n")
                        file.write(f"Token: {verify_response.get('data', {}).get('token', 'N/A')}\n")
                        file.write(f"Refresh Token: {verify_response.get('data', {}).get('refreshToken', 'N/A')}\n")
                        file.write("-" * 40 + "\n")
                    print(f'>\033[1;32m Account created and verified! \033[0m')
                else:
                    print(f'>\033[1;31m Verification failed: {verify_response} \033[0m')
            else:
                print(f'>\033[1;31m No verification code received \033[0m')
        else:
            print(f'>\033[1;31m Failed to send email: {create_account_response} \033[0m')
            
        print(f"\033[1;34m{'-' * 42}\033[0m")
        time.sleep(2)
        
    except KeyboardInterrupt:
        print('\n\033[1;33m Bot stopped by user\033[0m')
        break
    except Exception as e:
        print('\033[0m> \033[1;31mError :', str(e)[:100])
        print(f"\033[1;34m{'-' * 42}\033[0m")
        time.sleep(2)
