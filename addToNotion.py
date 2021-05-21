import requests
import json
import emoji


def postToNotion(title, name, children, databaseId = "7201475d4b6b494488cce0b9e249a788"):
  url = "https://api.notion.com/v1/pages"
  headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer secret_4rsw5maRnxEgmCAEZ5rJyRQJ4WGj0hr5bgZiXuYguB3'
  }
  requestBody = {
    "parent": {
      "database_id": databaseId
    },
    "properties": {
      "Name": {
        "title": [
          {
            "text": {
              "content": title
            }
          }
        ]
      },
      "From": {
          "select": {
              "name": name
          }
        }
    },
    "children": children
  }
  print(emoji.emojize(json.dumps(requestBody)))
  response = requests.request("POST", url, headers=headers, data=emoji.emojize(json.dumps(requestBody)).encode('utf-8'))
  print(response.status_code)
  if(response.status_code != 200):
    print('error while posting ' + title + ' to notion')
    print(response.text)
    return False
  return True


