from urllib.parse import urlparse
import re


def url_extract(message):
    """Extracts the full URL path from a given message and returns a constant trigger 'next'."""
    url_match = re.search(r"https?://[^\s]+", message)
    if not url_match:
        return None

    url = url_match.group(0)
    parsed_url = urlparse(url)

    # Extract full path as state
    full_path = parsed_url.netloc + parsed_url.path

    return full_path, "next"  # Returning state and constant trigger 'next'
