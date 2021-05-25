from addToNotion import postToNotion
from convertHtmlToNotion import parseHtmlToNotion
from sanitize import NotionSanitizer
import requests
import json
import html
import dateutil.parser as parser
import base64
from bs4 import BeautifulSoup
from simplegmail.message import Message

def getAccessToken(authCode):
  url = "https://oauth2.googleapis.com/token"

  payload = json.dumps({
    "code": authCode,
    "client_id": "891866724637-ajjtrcs38vo42f3s5s6vqq3tmplnd9qu.apps.googleusercontent.com",
    "client_secret": "Gu9-9xOCyTWXdhldOPYiyN65",
    "redirect_uri": "http://localhost:3000",
    "grant_type": "authorization_code"
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)
  return response.json()['access_token']


def getUserEmails(accessToken, labels = []):
  url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?labelIds=Label_5465479059402873463"

  payload={}
  headers = {
    'Authorization': 'Bearer {}'.format(accessToken)
  }

  response = requests.request("GET", url, headers=headers, data=payload)

  print(response.text)
  return response.text

def getUserEmail(accessToken, messageId):
  url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/17999d458efe362a"

  payload={}
  headers = {
    'Authorization': 'Bearer {}'.format(accessToken)
  }

  response = requests.request("GET", url, headers=headers, data=payload)

  return response.json()

def evaluate_message_payload(payload, msg_id):
  if 'attachmentId' in payload['body']:  # if it's an attachment
    return []
    # disabled attachments for now
    att_id = payload['body']['attachmentId']
    filename = payload['filename']
    if not filename:
        filename = 'unknown'

    obj = {
        'part_type': 'attachment',
        'filetype': payload['mimeType'],
        'filename': filename,
        'attachment_id': att_id,
        'data': None
    }

    if attachments == 'reference':
        return [obj]
    
    else:  # attachments == 'download'
        if 'data' in payload['body']:
            data = payload['body']['data']
        else:
            res = self.service.users().messages().attachments().get(
                userId=user_id, messageId=msg_id, id=att_id
            ).execute()
            data = res['data']

        file_data = base64.urlsafe_b64decode(data)
        obj['data'] = file_data
        return [obj]

  elif payload['mimeType'] == 'text/html':
      data = payload['body']['data']
      data = base64.urlsafe_b64decode(data)
      body = BeautifulSoup(data, 'lxml', from_encoding='utf-8').body
      return [{ 'part_type': 'html', 'body': str(body) }]

  elif payload['mimeType'] == 'text/plain':
      data = payload['body']['data']
      data = base64.urlsafe_b64decode(data)
      body = data.decode('UTF-8')
      return [{ 'part_type': 'plain', 'body': body }]

  elif payload['mimeType'].startswith('multipart'):
      ret = []
      if 'parts' in payload:
          for part in payload['parts']:
              ret.extend(evaluate_message_payload(part, msg_id))
      return ret

  return []

def addMailToNotion(accessToken):
  message = getUserEmail(accessToken, None)
  # response = json.load(response)
  print(message['id'])
  msg_id = message['id']
  thread_id = message['threadId']
  label_ids = []
  # if 'labelIds' in message:
  #     user_labels = {x.id: x for x in self.list_labels(user_id=user_id)}
  #     label_ids = [user_labels[x] for x in message['labelIds']]
  snippet = html.unescape(message['snippet'])

  payload = message['payload']
  headers = payload['headers']

  # Get header fields (date, from, to, subject)
  date = ''
  sender = ''
  recipient = ''
  subject = ''
  msg_hdrs = {}
  for hdr in headers:
      if hdr['name'] == 'Date':
          try:
              date = str(parser.parse(hdr['value']).astimezone())
          except Exception:
              date = hdr['value']
      elif hdr['name'] == 'From':
          sender = hdr['value']
      elif hdr['name'] == 'To':
          recipient = hdr['value']
      elif hdr['name'] == 'Subject':
          subject = hdr['value']
      
      msg_hdrs[hdr['name']] = hdr['value']

  parts = evaluate_message_payload(
      payload, msg_id
  )

  plain_msg = None
  html_msg = None
  attms = []
  for part in parts:
      if part['part_type'] == 'plain':
          if plain_msg is None:
              plain_msg = part['body']
          else:
              plain_msg += '\n' + part['body']
      elif part['part_type'] == 'html':
          if html_msg is None:
              html_msg = part['body']
          else:
              html_msg += '<br/>' + part['body']
      # elif part['part_type'] == 'attachment':
      #     attm = Attachment(self.service, user_id, msg_id,
      #                       part['attachment_id'], part['filename'],
      #                       part['filetype'], part['data'])
      #     attms.append(attm)
  new_message = Message("googleapiclient.discovery.Resource", "me", msg_id, thread_id, recipient, 
                sender, subject, date, snippet, plain_msg, html_msg, label_ids,
                attms, msg_hdrs)
  print(new_message)
  # print(new_message.html)
  sanitizer = NotionSanitizer()
  sanitizedMessage = sanitizer.sanitizeString(new_message.html)
  notionBlocks = parseHtmlToNotion(sanitizedMessage)
  success = postToNotion(new_message.subject, "James Clear", notionBlocks, "7201475d4b6b494488cce0b9e249a788", "secret_4rsw5maRnxEgmCAEZ5rJyRQJ4WGj0hr5bgZiXuYguB3")
