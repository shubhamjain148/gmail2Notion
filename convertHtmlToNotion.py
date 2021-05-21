from html.parser import HTMLParser

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

singleTags = ["br"]

def findOpenAnnotationTags(openTags):
    openAnnotationTags = []
    for tag in openTags:
        if(tag in annotationMapping):
            openAnnotationTags.append(tag)
    return openAnnotationTags
  

def parseHtmlToNotion(htmlString):

  class NotionHtmlParser(HTMLParser):
    children = []
    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
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
        # print("Encountered an end tag :", tag)
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
            self.children.append(self.currentBlock)
            self.currentBlock = {}
        
        # if condition is not true that means it was a closing 
        # single tag like <image />
        if(self.openTags[len(self.openTags) - 1] == tag):
            self.openTags.pop()

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        self.currentData = self.currentData + data

    def __init__(self, *, convert_charrefs: bool) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.currentBlock = {}
        self.currentBlockChildren = []
        self.openTags = []
        self.currentChildOfBlock = {}
        self.currentData = ""
        self.currentLink = None
        self.isLiOpen = False
      
  parser = NotionHtmlParser(convert_charrefs=False)
  parser.feed(htmlString)
  children = parser.children
  parser.close()
  return children
