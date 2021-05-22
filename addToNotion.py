import requests
import json
import emoji


def postToNotion(title, name, children, databaseId, integrationKey):
  url = "https://api.notion.com/v1/pages"
  headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer {}'.format(integrationKey)
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
  response = requests.request("POST", url, headers=headers, data=emoji.emojize(json.dumps(requestBody)).encode('utf-8'))
  print(response.status_code)
  if(response.status_code != 200):
    print('error while posting ' + title + ' to notion')
    print(response.text)
    return False
  return True


