import requests
import json

def postToNotion(title, children, databaseId):

  url = "https://api.notion.com/v1/pages"
  headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer token'
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
          }
      },
      "children": children
  }
  response = requests.request("POST", url, headers=headers, data=json.dumps(requestBody))
  print(response.text)

