"""
Browser Activity Extractor

A unified web activity extractor that works with both Firefox and Chrome history entries.
This script extracts meaningful information about web activities including:
- Downloads
- Searches
- General web access

It handles the different formats used by Firefox (with Transition markers) and 
Chrome (with Type indicators) to provide consistent output.
"""

import re
from urllib.parse import urlparse, parse_qs, unquote


def browser_activity_extract(message, source_long=None):
    """
    Extract web activity information from browser history entries.

    This function handles both Firefox and Chrome history formats by looking
    for browser-specific patterns in the message and extracting meaningful state
    and trigger information.

    Args:
        message (str): The browser history message to analyze
        source_long (str, optional): The source_long field that indicates browser type

    Returns:
        tuple or None: A tuple of (state, trigger) or None if no meaningful activity detected
    """
    # Skip if message is empty
    if not message:
        return None

    # Extract URL from the message
    url_match = re.search(r'(https?://[^\s)]+)', message)
    if not url_match:
        return None

    url = url_match.group(1)
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()
    path = parsed_url.path

    # Determine browser type (default to unknown if not specified)
    is_firefox = source_long and 'firefox' in source_long.lower()
    is_chrome = source_long and 'chrome' in source_long.lower()

    # Extract the title if present (common pattern in both browsers)
    title = None
    title_match = re.search(r'\(([^)]+)\)', message)
    if title_match:
        title = title_match.group(1)

    # CASE 1: Handle Downloads
    if _is_download_activity(message, parsed_url, is_firefox, is_chrome):
        return _extract_download_info(message, parsed_url, title)

    # CASE 2: Handle Searches
    search_result = _extract_search_info(message, parsed_url, title)
    if search_result:
        return search_result

    # CASE 3: Handle general web access
    return _extract_web_access_info(message, netloc, path, is_firefox, is_chrome)


def _is_download_activity(message, parsed_url, is_firefox, is_chrome):
    """
    Determine if the activity is a download based on browser-specific patterns.

    Args:
        message (str): The browser history message
        parsed_url (ParseResult): The parsed URL
        is_firefox (bool): Whether this is a Firefox history entry
        is_chrome (bool): Whether this is a Chrome history entry

    Returns:
        bool: True if this is a download activity
    """
    # Check for Firefox-specific download transition
    if is_firefox and 'Transition: DOWNLOAD' in message:
        return True

    # For both browsers, look for download-related patterns
    path_lower = parsed_url.path.lower()

    # Check for common download extensions in the URL path
    download_extensions = ['.zip', '.tar.gz', '.exe',
                           '.dmg', '.deb', '.msi', '.pdf', '.apk', '.rpm', '.pkg']
    if any(path_lower.endswith(ext) for ext in download_extensions):
        return True

    # Look for download indicators in titles and URLs
    download_indicators = ['download', 'install',
                           'setup', '.exe', '.dmg', '.deb', '.msi', '.zip']

    # Check in URL path
    if any(indicator in path_lower for indicator in download_indicators):
        return True

    # Check in page title if available
    title_match = re.search(r'\(([^)]+)\)', message)
    if title_match:
        title = title_match.group(1).lower()
        if any(indicator in title for indicator in download_indicators):
            # Exclude search results for downloads
            if 'search' in message.lower() and ('q=' in message or 'query=' in message):
                # This is likely a search for downloads, not an actual download
                return False
            return True

    return False


def _extract_download_info(message, parsed_url, title):
    """
    Extract download information like filename for download activities.

    Args:
        message (str): The browser history message
        parsed_url (ParseResult): The parsed URL
        title (str): The page title if available

    Returns:
        tuple: (filename, trigger)
    """
    # Try to extract filename from parentheses for common download files
    filename_match = re.search(
        r'\(([^)]+\.(zip|tar\.gz|dmg|exe|deb|msi|pdf|apk|rpm|pkg))\)', message)

    if filename_match:
        filename = filename_match.group(1)
    else:
        # Extract from path if no match in title
        path = parsed_url.path
        path_parts = path.split('/')

        # Get the last non-empty part of the path
        potential_filename = next(
            (part for part in reversed(path_parts) if part), "unknown_file")

        # If there are query parameters, remove them
        potential_filename = potential_filename.split('?')[0]

        # If we can't find a proper filename, use the domain + "download"
        if potential_filename == "unknown_file" or not potential_filename:
            domain = parsed_url.netloc.replace('www.', '')
            potential_filename = f"{domain}_download"

        filename = potential_filename

    # Clean filename of any URL encoding or special characters
    filename = unquote(filename)
    filename = re.sub(r'[^\w\.-]', '_', filename)

    return filename, "downloaded_file"


def _extract_search_info(message, parsed_url, title):
    """
    Extract search query information from URLs that point to search engines.

    Args:
        message (str): The browser history message
        parsed_url (ParseResult): The parsed URL
        title (str): The page title if available

    Returns:
        tuple or None: (search_query, search_trigger) or None if not a search
    """
    netloc = parsed_url.netloc.lower()
    path = parsed_url.path.lower()

    # Check if this looks like a search engine URL
    is_search_url = False
    search_engine = "unknown"

    # Check common search engines
    if 'google.com' in netloc and '/search' in path:
        is_search_url = True
        search_engine = "google"
    elif 'bing.com' in netloc and '/search' in path:
        is_search_url = True
        search_engine = "bing"
    elif 'yahoo.com' in netloc and '/search' in path:
        is_search_url = True
        search_engine = "yahoo"
    elif 'duckduckgo.com' in netloc and '/search' in path:
        is_search_url = True
        search_engine = "duckduckgo"
    # Generic checks for other search engines
    elif '/search' in path and ('q=' in parsed_url.query or 'query=' in parsed_url.query or 'p=' in parsed_url.query):
        is_search_url = True
        # Try to extract search engine name from domain
        parts = netloc.split('.')
        if len(parts) >= 2:
            search_engine = parts[-2]  # e.g., google.com -> google

    if not is_search_url:
        return None

    # Extract search parameters
    query_params = parse_qs(parsed_url.query)

    # Different search engines use different query parameters
    query_param = None

    if search_engine == "google":
        query_param = 'q'
    elif search_engine == "bing":
        query_param = 'q'
    elif search_engine == "yahoo":
        query_param = 'p'
    elif search_engine == "duckduckgo":
        query_param = 'q'
    else:
        # Try common query parameters
        for param in ['q', 'query', 'p', 'text', 'search']:
            if param in query_params and query_params[param]:
                query_param = param
                break

    # If we identified a query parameter
    if query_param and query_param in query_params and query_params[query_param]:
        search_query = unquote(query_params[query_param][0]).replace('+', ' ')

        # Clean the query to remove special characters but preserve spaces and punctuation
        search_query = re.sub(r'[^\w\s.,?!-]', '', search_query)

        # Return the query as state and engine-specific search trigger
        return search_query, f"performed_{search_engine}_search"

    # If we can't extract the query but this is definitely a search page
    # (e.g., maybe there's no query parameter in the URL)
    if title and "search" in title.lower():
        # Extract potential search terms from the title
        # Commonly titles are in format "search terms - Search Engine Name"
        title_parts = title.split(' - ')
        if len(title_parts) > 0:
            return title_parts[0], f"performed_{search_engine}_search"

    # If we still can't find a search query
    return f"{netloc}/search", "performed_search"


def _extract_web_access_info(message, netloc, path, is_firefox, is_chrome):
    """
    Format web access activity with domain and path information, determining
    the access method based on browser-specific indicators.

    Args:
        message (str): The browser history message
        netloc (str): The domain
        path (str): The URL path
        is_firefox (bool): Whether this is a Firefox history entry
        is_chrome (bool): Whether this is a Chrome history entry

    Returns:
        tuple: (website_info, access_trigger)
    """
    # Extract domain (remove www. prefix)
    domain = netloc
    if domain.startswith('www.'):
        domain = domain[4:]

    # Format the path - take up to 3 segments
    path_segments = [segment for segment in path.split('/') if segment]
    path_segments = path_segments[:3]  # Limit to 3 segments

    # Create the state string
    if path_segments:
        state = f"{domain}/{'/'.join(path_segments)}"
    else:
        state = domain

    # Determine the access method (trigger)
    if is_firefox:
        # Firefox uses explicit transition types
        if 'Transition: TYPED' in message:
            return state, "accessed_website_direct"
        elif 'Transition: LINK' in message:
            return state, "accessed_website_link"
        elif 'Transition: REDIRECT' in message:
            return state, "accessed_website_redirect"
        else:
            # Default for Firefox
            return state, "accessed_website"
    elif is_chrome:
        # Chrome uses Type: indicators
        if 'Type: [GENERATED' in message:
            return state, "accessed_website_direct"
        elif 'Type: [LINK' in message:
            return state, "accessed_website_link"
        elif 'Type: [REDIRECT' in message:
            return state, "accessed_website_redirect"
        else:
            # Default for Chrome
            return state, "accessed_website"
    else:
        # Generic case for unknown browser type
        return state, "accessed_website"
