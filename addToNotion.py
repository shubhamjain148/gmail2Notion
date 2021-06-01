import requests
import json
import emoji

def getNotionHeader(integration_key):
  return {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer {}'.format(integration_key)
  }


def postToNotion(title, extraDetails, children, databaseId, integrationKey):
  url = "https://api.notion.com/v1/pages"
  headers = getNotionHeader(integrationKey)
  requestBody = {
    "parent": {
      "database_id": databaseId
    },
    "properties": extraDetails,
    "children": children
  }
  print(extraDetails)
  response = requests.request("POST", url, headers=headers, data=emoji.emojize(json.dumps(requestBody)).encode('utf-8'))
  print(response.status_code)
  if(response.status_code != 200):
    print('error while posting ' + title + ' to notion')
    print(response.text)
    return False
  return True

def getDatabaseDetails(integration_key, database_id):
  headers = getNotionHeader(integration_key)
  url = 'https://api.notion.com/v1/databases/{}'.format(database_id)
  response = requests.request("GET", url=url, headers=headers)
  print(response.text)
  return response


