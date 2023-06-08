import requests

def get_fanpage_access_token():
  app_id = 'YOUR APP ID'
  target_fanpage_id = 'TARGET FANPAGE ID'
  app_secret = 'YOUR APP SECRET'
  user_access_token = 'YOUR USER ACCESS TOKEN'

  url = 'https://graph.facebook.com/oauth/access_token'
  params = {
    'grant_type': 'fb_exchange_token',
    'client_id': app_id,
    'client_secret': app_secret,
    'fb_exchange_token': user_access_token
  }
  response = requests.get(url, params=params)
  long_life_user_access_token = response.json()['access_token']

  url =  f'https://graph.facebook.com/{target_fanpage_id}?fields=access_token&access_token={long_life_user_access_token}'

  response = requests.get(url)
  fanpage_access_token = response.json()['access_token']

  with open('fanpage_access_token.txt', 'w') as f:
    f.write(fanpage_access_token)

if __name__ == '__main__':
  pass
