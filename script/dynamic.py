import re
from urllib.parse import urlparse

# Define specific triggers for different web actions
TRIGGER_MAPPING = {
    "download_firefox_installer": "downloaded_firefox_installer",
    "search_google": "searched_google",
    "search_firefox": "searched_firefox",
    "open_bing": "opened_bing",
    "open_mozilla": "opened_mozilla",
    "open_google": "opened_google",
    "open_web": "opened_web"
}


def dynamic_extract(message):
    """
    Extracts the relevant state and assigns a trigger based on predefined rules.

    Rules (Ordered from Most Specific to Least Specific):
    1. Downloading Firefox Installer -> "downloaded_firefox_installer"
    2. Searching Google -> "searched_google"
    3. Searching in Firefox (any search engine) -> "searched_firefox"
    4. Opening Bing -> "opened_bing"
    5. Opening Mozilla.org -> "opened_mozilla"
    6. Opening Google Homepage -> "opened_google"
    7. General Web Visit -> "opened_web"
    """

    # Detect URLs
    url_match = re.search(r"https?://[^\s]+", message)
    if not url_match:
        return None  # Skip non-web-related messages

    url = url_match.group(0)
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()

    # Rule 1: Downloading Firefox Installer (Most Specific)
    if "mozilla.org" in netloc and "firefox/download" in parsed_url.path:
        return netloc, TRIGGER_MAPPING["download_firefox_installer"]

    # Rule 2: Searching on Google
    if "google.com" in netloc and ("search" in parsed_url.path or "q=" in parsed_url.query):
        return netloc, TRIGGER_MAPPING["search_google"]

    # Rule 3: Searching in Firefox (Assuming it's any search query)
    if "search" in parsed_url.path or "q=" in parsed_url.query:
        return netloc, TRIGGER_MAPPING["search_firefox"]

    # Rule 4: Opening Bing
    if "bing.com" in netloc:
        return netloc, TRIGGER_MAPPING["open_bing"]

    # Rule 5: Opening Mozilla.org
    if "mozilla.org" in netloc:
        return netloc, TRIGGER_MAPPING["open_mozilla"]

    # Rule 6: Opening Google Homepage
    if "google.com" in netloc:
        return netloc, TRIGGER_MAPPING["open_google"]

    # Rule 7: General Web Visit (Least Specific)
    return netloc, TRIGGER_MAPPING["open_web"]
