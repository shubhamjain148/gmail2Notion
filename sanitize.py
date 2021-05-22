
from html_sanitizer.sanitizer import Sanitizer
import emoji


class NotionSanitizer():
  sanitizer = None
  
  def __init__(self) -> None:
    self.sanitizer = Sanitizer({
    "tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "hr", 'u', 'code', 'br', 'div', 'span'
        },
    "separate": {
        "a", "p", "li", "span"
        }
    })
    
  def sanitizeString(self, string: str) -> str:
    demojizedString: str = emoji.demojize(string)
    return self.sanitizer.sanitize(demojizedString)