import requests
import json


def postToNotion(title, name, children, databaseId = "defaultDatabaseId"):
  url = "https://api.notion.com/v1/pages"
  headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer <integrationKey>'
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
  response = requests.request("POST", url, headers=headers, data=json.dumps(requestBody))
  print(response.status_code)
  if(response.status_code != 200):
    print('error while posting ' + title + ' to notion')
    print(response.text)
    return False
  return True


