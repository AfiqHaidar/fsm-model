import re
from urllib.parse import urlparse


def url_extract(message):
    """Extract full URL path from a message."""
    url_match = re.search(r"https?://[^\s]+", message)
    if not url_match:
        return None

    parsed_url = urlparse(url_match.group(0))
    return parsed_url.netloc + parsed_url.path  # Extracts domain + path
