import re
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except:
        return False

def sanitize_url(url):
    # Basic sanitization – remove dangerous characters
    return re.sub(r'[<>"\']', '', url)