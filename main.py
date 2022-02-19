import requests
import os;
import time;
from dotenv import load_dotenv
load_dotenv()

def send_request(relative_url):
  return client.get(f'{base_url}{relative_url}')

def setup_user_id_associations():
  users_res = send_request('users.list?pretty=1')
  global users
  members = users_res.json()['members']

  for user in members:
    users[user['id']] = user

def setup_messages():
  global messages
  first_run = True
  cursor = ''

  while cursor or first_run:
    first_run = False
    chat_res = send_request(f'conversations.history?channel={channel}&limit=500&pretty=1&oldest=1{f"&cursor={cursor}" if cursor else ""}')
    chat_json = chat_res.json()
    cursor = chat_json.get('response_metadata').get('next_cursor') if 'response_metadata' in chat_json and 'next_cursor' in chat_json.get('response_metadata') else None
    
    for message in chat_json['messages']:
      messages.insert(0, message)

def setup_file_string():
  global messages
  global file_text

  for message in messages:
    user_real_name = users[message['user']]['real_name']

    if 'subtype' in message and message['subtype'] == 'channel_join':
      continue

    file_text += f'{user_real_name}: {message["text"]}\n'
    replies_res = send_request(f'conversations.replies?channel={channel}&ts={message["ts"]}')
    replies_json = replies_res.json()
    replies = replies_json['messages'] if 'messages' in replies_json else None

    if replies:
      replies.pop(0)
      for reply in replies:
        file_text += f'\t\t{users[reply["user"]]["real_name"]}: {reply["text"]}\n'
    
    file_text += '\n'

def save_messages_to_file():
  file = open(f'slackchat_{time.time()}', 'w')
  file.write(file_text)
  file.close()

channel = input('Enter channelID here: ')
messages = []
users = {}
file_text = ''
base_url = 'https://slack.com/api/'
client = requests.Session()
client.headers = {'Authorization': f'Bearer {os.environ.get("BTOKEN")}'}

setup_user_id_associations()
setup_messages()
setup_file_string()
save_messages_to_file()

