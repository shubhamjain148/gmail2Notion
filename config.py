import json

def getLabelMappings():
  labelFile = open('labelMappings.json')
  return json.load(labelFile)