import json
from html_sanitizer import Sanitizer

def getLabelMappings():
  labelFile = open('labelMappings.json')
  return json.load(labelFile)

def getSanitizer():
  return Sanitizer({
    "tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "hr", 'u', 'code', 'br', 'div', 'span'
        },
    "separate": {
        "a", "p", "li", "span"
        }
    })