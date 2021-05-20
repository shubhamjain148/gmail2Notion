from addToNotion import postToNotion
from simplegmail import Gmail
from html_sanitizer import Sanitizer
from html.parser import HTMLParser

mappings = {
    "p": "paragraph",
    "br": "paragraph",
    "h1": "heading_1",
    "h2": "heading_2",
    "h3": "heading_3",
    "div": "paragraph",
    "li": "bulleted_list_item"
}

annotationMapping = {
    "strong": "bold",
    "em": "italic",
    "u": "underline",
    "code": "code"
}

labelMappings = {
    "Readings/James Clear": "James Clear",
    "Readings/George Mack": "George Mack"
}

name = "Readings/James Clear"


children = []

def findOpenAnnotationTags(openTags):
    openAnnotationTags = []
    for tag in openTags:
        if(tag in annotationMapping):
            openAnnotationTags.append(tag)
    return openAnnotationTags

def findOpenBaseTag(openTags):
    for tag in openTags:
        if(tag in mappings):
            return tag
    return None

# TODO: Improve the parsing algo
class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        parsedAttrbs = {}
        for attr in attrs:
            parsedAttrbs[attr[0]] = attr[1]
        if(tag == "a" and "href" in parsedAttrbs and parsedAttrbs["href"] != None):
            self.currentLink = parsedAttrbs["href"]

        if(self.currentData.strip() != ""):
            openAnnotationTags = findOpenAnnotationTags(self.openTags)
            self.currentChildOfBlock = {
                "type": "text",
                "annotations": {},
                "text": {
                    "content": self.currentData
                }
            }
            for openAnnotationTag in openAnnotationTags:
                self.currentChildOfBlock["annotations"][annotationMapping[openAnnotationTag]] = True
            self.currentBlockChildren.append(self.currentChildOfBlock)
            self.currentChildOfBlock = {}
            self.currentData = ""
        if(tag == "br"):
            self.currentBlock = {
                "object": "block",
                "type": mappings[tag]
            }
            self.currentBlock[self.currentBlock["type"]] = {
                "text": self.currentBlockChildren
            }
            self.currentBlockChildren = []
            children.append(self.currentBlock)
            self.currentBlock = {}
        self.openTags.append(tag)

    def handle_endtag(self, tag):
        global children
        # print("Encountered an end tag :", tag)
        if(self.currentData.strip() != ""):
            self.currentChildOfBlock = {
                "type": "text",
                "text": {
                    "content": self.currentData
                }
            }
            self.currentData = ""
            if (tag in annotationMapping):
                self.currentChildOfBlock["annotations"] = {
                    annotationMapping[tag]: True
                }
            if(self.currentLink != None):
                self.currentChildOfBlock["text"]["link"] = {
                    "url": self.currentLink
                }
            self.currentBlockChildren.append(self.currentChildOfBlock)
            self.currentChildOfBlock = {}
        if (tag in mappings or tag== "br"):
            type = mappings[tag]
            if(tag == "li" and len(self.openTags) > 1 and self.openTags[len(self.openTags) - 2] == "ol"):
                type = "numbered_list_item"
            self.currentBlock = {
                "object": "block",
                "type": type
            }
            self.currentBlock[self.currentBlock["type"]] = {
                "text": self.currentBlockChildren
            }
            self.currentBlockChildren = []
            children.append(self.currentBlock)
            self.currentBlock = {}
        
        if(tag == "a"):
            self.currentLink = None
        self.openTags.pop()

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        self.currentData = data

    def __init__(self, *, convert_charrefs: bool) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.children = []
        self.currentBlock = {}
        self.currentBlockChildren = []
        self.openTags = []
        self.currentChildOfBlock = {}
        self.currentData = ""
        self.currentLink = None


parser = MyHTMLParser(convert_charrefs=False)


gmail = Gmail()

# Unread messages in inbox with label "Work"
labels = gmail.list_labels()

for labelName, name in labelMappings.items():
    print('Processing label {}'.format(labelName))
    work_label = list(filter(lambda x: x.name == labelName, labels))[0]
    messages = gmail.get_unread_messages(labels=[work_label])
    sanitizer = Sanitizer({"tags": {
            "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
            "li", "br", "hr", "div", 'u', 'code', 'br'
        },})

    print('Found {} unread emails for label {}'.format(len(messages), labelName))

    for message in messages:
        print(message.label_ids)
        htmlMessage = message.html
        sanitizeHtmlMessage = sanitizer.sanitize(htmlMessage)
        children = []
        parser.feed(sanitizeHtmlMessage.strip())
        success = postToNotion(message.subject, name, children)
        if(success):
            message.mark_as_read()

