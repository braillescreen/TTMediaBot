#!/usr/bin/env python3

import requests
from getpass import getpass

class AuthenticationError(Exception):
    pass

class PhoneValidationError(Exception):
    pass

class TokenValidationError(Exception):
    pass

client_id = '2274003'
client_secret = 'hHbZxrka2uZ6jB1inYsH'
api_ver='5.68'
scope = 'all'
user_agent = 'VKAndroidApp/4.13.1-1206 (Android 7.1.1; SDK 25; armeabi-v7a; ; ru)'
api_url = 'https://api.vk.com/method/'
receipt = 'fkdoOMX_yqQ:APA91bHbLn41RMJmAbuFjqLg5K-QW7si9KajBGCDJxcpzbuvEcPIk9rwx5HWa1yo1pTzpaKL50mXiWvtqApBzymO2sRKlyRiWqqzjMTXUyA5HnRJZyXWWGPX8GkFxQQ4bLrDCcnb93pn'

def request_auth(login, password, scope='', code=''):
    if not (login or password):
        raise ValueError
    url = 'https://oauth.vk.com/token?grant_type=password&client_id='+client_id+'&client_secret='+client_secret+'&username='+login+'&password='+password+'&v='+api_ver+'&2fa_supported=1&force_sms=1'
    if scope:
        url += '&scope=' + scope
    if code:
        url += '&code=' + code
    headers = {
    'User-Agent': user_agent
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and 'access_token' in r.text:
        res = r.json()
        access_token = res['access_token']
        return access_token
    elif 'need_validation' in r.text:
        res = r.json()
        sid = res['validation_sid']
        code = handle_2fa(sid)
        access_token = request_auth(login, password, scope=scope,  code=code)
        return access_token
    else:
        raise AuthenticationError(r.text)

def handle_2fa(sid):
    if not sid:
        raise ValueError('No sid is given')
    url = api_url+'auth.validatePhone?sid='+sid+'&v='+api_ver
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        print('Two factor authentication is required')
        code = ''
        while not code:
            code = input('SMS code: ')
            if len(code) != 6 or not code.isdigit():
                print('SMS code must be a string of 6 digits')
                continue
            return code
    else:
        raise PhoneValidationError(r.text)

def validate_token(token, receipt):
    if not (token and receipt):
        raise ValueError('Required argument is missing')
    url = api_url+'auth.refreshToken?access_token='+token+'&receipt='+receipt+'&v='+api_ver
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and 'token' in r.text:
        res = r.json()
        received_token = res['response']['token']
        if token == received_token or not received_token:
            raise TokenValidationError(r.text)
        else:
            return received_token
    else:
        raise TokenValidationError(r.text)

def main():
    login = ''
    password = ''
    try:
        print('VK Authentication Helper for TTMediaBot')
        print()
        print('Enter your VK credentials to continue')
        while not login:
            login = input('Phone, email or  login: ')
        while not password:
            password = getpass('Password: ')
        token = request_auth(login, password, scope=scope)
        validated_token = validate_token(token, receipt)
        print('Your VK token:')
        print(validated_token)
    except Exception as e:
        print(e)
    input('Press any key to continue')

if __name__ == '__main__':
    main()
