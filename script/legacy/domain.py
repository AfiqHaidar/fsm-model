from urllib.parse import urlparse
import re


def domain_extract(message):
    """Extracts the domain from a given message and returns a constant trigger 'next'."""
    url_match = re.search(r"https?://[^\s]+", message)
    if not url_match:
        return None

    url = url_match.group(0)
    parsed_url = urlparse(url)

    # Extract domain
    domain = parsed_url.netloc.strip()

    return domain, "next"  # Returning state and constant trigger 'next'
