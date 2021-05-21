from addToNotion import postToNotion
from simplegmail import Gmail
from html_sanitizer import Sanitizer
from html.parser import HTMLParser
import emoji

# TODO: add support for path params for database id and integration key
mappings = {
    "p": "paragraph",
    "h1": "heading_1",
    "h2": "heading_2",
    "h3": "heading_3",
    "div": "paragraph",
    "li": "bulleted_list_item",
    "ul": "paragraph", # for text sitting inside ul not inside li
    "ol": "paragraph", # for text sitting inside ul not inside li
    "span": "paragraph"
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

singleTags = ["br"]

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
        print("Encountered a start tag:", tag)
        if tag == "li":
            self.isLiOpen = True
        parsedAttrbs = {}
        for attr in attrs:
            parsedAttrbs[attr[0]] = attr[1]
        if(tag == "a" and "href" in parsedAttrbs and parsedAttrbs["href"] != None):
            self.currentLink = parsedAttrbs["href"]
        
        if(self.currentData.strip(" ") != ""):
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
        if(tag == "br"):
            self.currentData = "\n"
        else:
            self.currentData = ""
        if(tag not in singleTags):
            self.openTags.append(tag)

    def handle_endtag(self, tag):
        global children
        print("Encountered an end tag :", tag)
        if(self.currentData.strip(" ") != ""):
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
            self.currentData = ""
            if(self.currentLink != None):
                self.currentChildOfBlock["text"]["link"] = {
                    "url": self.currentLink
                }
            self.currentBlockChildren.append(self.currentChildOfBlock)
            self.currentChildOfBlock = {}
            
        if(tag == "a"):
            self.currentLink = None
            
        if(self.isLiOpen):
            # if br in between li then insert new line to li text
            if(tag != "li"):
                if(self.openTags[len(self.openTags) -1] == tag):
                    self.openTags.pop()
                return
            else:
                self.isLiOpen = False
                
        if (tag in mappings):
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
        
        # if condition is not true that means it was a closing 
        # single tag like <image />
        if(self.openTags[len(self.openTags) - 1] == tag):
            self.openTags.pop()

    def handle_data(self, data):
        print("Encountered some data  :", data)
        self.currentData = self.currentData + data

    def __init__(self, *, convert_charrefs: bool) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.children = []
        self.currentBlock = {}
        self.currentBlockChildren = []
        self.openTags = []
        self.currentChildOfBlock = {}
        self.currentData = ""
        self.currentLink = None
        self.isLiOpen = False


parser = MyHTMLParser(convert_charrefs=False)


gmail = Gmail()

# # Unread messages in inbox with label "Work"
labels = gmail.list_labels()

sanitizer = Sanitizer({
    "tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "hr", 'u', 'code', 'br', 'div', 'span'
        },
    "separate": {
        "a", "p", "li", "span"
        }
    })

for labelName, name in labelMappings.items():
    print('Processing label {}'.format(labelName))
    work_label = list(filter(lambda x: x.name == labelName, labels))[0]
    messages = gmail.get_unread_messages(labels=[work_label])
    print('Found {} unread emails for label {}'.format(len(messages), labelName))

    for message in messages:
        htmlMessage = message.html
        htmlMessageWithoutEmoji = emoji.demojize(htmlMessage)
        print("-----------------------------------------------------")
        sanitizeHtmlMessage = sanitizer.sanitize(htmlMessageWithoutEmoji)
        print(sanitizeHtmlMessage)
        print("-----------------------------------------------------")
        children = []
        parser.feed(sanitizeHtmlMessage.strip())
        # print(children)
        success = postToNotion(message.subject, name, children)
        if(success):
            message.mark_as_read()
