from addToNotion import postToNotion
from simplegmail import Gmail
from html_sanitizer import Sanitizer
from html.parser import HTMLParser
import pprint

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

# TODO: Solve for tag inside tag
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
            if(tag == "li"):
                print(tag)
                print(self.openTags)
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
# print(labels)
work_label = list(filter(lambda x: x.name == 'Readings/James Clear', labels))[0]

messages = gmail.get_messages(labels=[work_label])
# print("To: " + messages[0].recipient)
# print("From: " + messages[0].sender)
# print("Subject: " + messages[0].subject)
# print("Date: " + messages[0].date)
# print("Preview: " + messages[0].snippet)
# markdown = html2markdown.convert(messages[0].html)


# {
#   'tags': ('h1', 'h2', 'h3', 'p', 'ul', 'li', 'ol', 'a', 'strong', 'em', 'li', 'br'),
#   'attributes': {"a": ("href", "name", "target", "title", "id", "rel")},
#   "whitespace": {"br"},
#   'empty': set(),
#   'separate': set(),
#   "element_preprocessors": [
#         # convert span elements into em/strong if a matching style rule
#         # has been found. strong has precedence, strong & em at the same
#         # time is not supported
#         bold_span_to_strong,
#         italic_span_to_em,
#         tag_replacer("b", "strong"),
#         tag_replacer("i", "em"),
#         tag_replacer("form", "p"),
#         target_blank_noopener,
#     ]
# }

sanitizer = Sanitizer({"tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "hr", "div", 'u', 'code', 'br'
    },})



# print(sanitizeHtmlMessage)

# sanitizeHtmlMessage = '<h2><strong>How to Choose a Habit that Sticks</strong></h2> <p>The most important decision you will make is what habit to build. </p> <p>Pick the right habit and progress is easy. Pick the wrong habit and life is a struggle. It is much more important to work on the right habit than it is to work really hard. (Working hard is still important, of course.) </p> <p>In this lesson, we’re going to discuss how to choose the right habit for you.</p> <p>When most people think about the habits they want to build, they naturally start by considering the outcomes they want to achieve. "I want to lose weight." Or, "I want to stop smoking."</p> <p>The alternative is to build what I call “<strong>identity-based habits</strong>” and start by focusing on who we wish to become, not what we want to achieve. (This is an idea I unpack more fully in Chapter 2 of <a href="https://click.convertkit-mail4.com/75u08p78n3u2uz8x8ocz/25h2hoh70p82eks3/aHR0cHM6Ly9qYW1lc2NsZWFyLmNvbS9hdG9taWMtaGFiaXRz" rel="noopener noreferrer" target="_blank"><em>Atomic Habits</em></a>.)</p>'


for message in messages:
    htmlMessage = message.html
    sanitizeHtmlMessage = sanitizer.sanitize(htmlMessage)
    children = []
    parser.feed(sanitizeHtmlMessage.strip())
    postToNotion(message.subject, children, "7201475d4b6b494488cce0b9e249a788")
# print(children)