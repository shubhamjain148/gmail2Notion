from convertHtmlToNotion import parseHtmlToNotion
from config import getLabelMappings, getSanitizer
from addToNotion import postToNotion
from simplegmail import Gmail
import emoji

# TODO: add support for path params for database id and integration key


sanitizer = getSanitizer()

labelMappings = getLabelMappings()
gmail = Gmail()
labels = gmail.list_labels()

for labelName, name in labelMappings.items():
    print('Processing label {}'.format(labelName))
    work_labels = list(filter(lambda x: x.name == labelName, labels))
    if(len(work_labels) == 0):
        print('No label with name {} found in gmail'.format(labelName))
        continue
    work_label = work_labels[0]
    messages = gmail.get_unread_messages(labels=[work_label])
    print('Found {} unread emails for label {}'.format(len(messages), labelName))
    for message in messages:
        htmlMessage = message.html
        htmlMessageWithoutEmoji = emoji.demojize(htmlMessage)
        sanitizeHtmlMessage = sanitizer.sanitize(htmlMessageWithoutEmoji)
        children = parseHtmlToNotion(sanitizeHtmlMessage.strip())
        success = postToNotion(message.subject, name, children)
        if(success):
            message.mark_as_read()
