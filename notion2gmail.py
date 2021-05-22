from addToNotion import postToNotion
import argparse
from typing import List
from simplegmail.label import Label

from simplegmail.message import Message
from convertHtmlToNotion import parseHtmlToNotion

from readEmail import GmailReader
from config import getLabelMappings
from sanitize import NotionSanitizer

parser = argparse.ArgumentParser(description="Move emails from gmail to notion and create a reading list")

parser.add_argument('id', 
                    metavar="databaseId",
                    type=str,
                    help="id of the database into which the emails should be added")

parser.add_argument('key',
                    metavar="integration_key",
                    type=str,
                    help="secret key of the integration with which database was shared")

args = parser.parse_args()

labelMappings = getLabelMappings()
gmail = GmailReader()
sanitizer = NotionSanitizer()

for label, name in labelMappings.items():
  labelInGmail: Label = gmail.getGmailLabel(label)
  if(labelInGmail == None):
    print("Label {} not present in gmail", label)
  labelMessages: List[Message] = gmail.getUnreadEmailsForLabel(labelInGmail)
  for message in labelMessages:
    sanitizedMessage = sanitizer.sanitizeString(message.html)
    notionBlocks = parseHtmlToNotion(sanitizedMessage)
    success = postToNotion(message.subject, name, notionBlocks, args.id, args.key)
    if(success):
      message.mark_as_read()
  
