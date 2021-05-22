from typing import List
from simplegmail.label import Label
from simplegmail.message import Message
from simplegmail import Gmail
class GmailReader():
  labels = []
  gmail = None
  
  def __init__(self) -> None:
    self.gmail = Gmail()
    self.labels = self.gmail.list_labels()
  
  def getGmailLabel(self, label) -> Label:
    work_labels = list(filter(lambda x: x.name == label, self.labels))
    if(len(work_labels) == 0):
      return None
    return work_labels[0]
  
  def getUnreadEmailsForLabel(self,label) -> List[Message]:
    messages = self.gmail.get_unread_messages(labels=[label])
    return messages