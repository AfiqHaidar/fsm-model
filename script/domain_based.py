import re
from urllib.parse import urlparse


def domain_extract(message):
    """Extract domain from a message containing a URL."""
    url_match = re.search(r"https?://[^\s]+", message)
    if not url_match:
        return None

    parsed_url = urlparse(url_match.group(0))
    return parsed_url.netloc.strip()  # Extracts only the domain
