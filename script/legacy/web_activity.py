import re
from urllib.parse import urlparse, parse_qs, unquote


def web_activity_extract(message):
    """
    Extracts web activity based on "Transition:" patterns in the message.

    Handles three main types of web activity:
    1. Downloads - Extracts filename and assigns "downloaded_file" trigger
    2. Searches - Extracts search queries and assigns search engine-specific triggers
    3. General Web Access - Extracts domain and path for general website access

    Returns a tuple of (state, trigger) where:
    - state: A string representing the activity (filename, search query, or website)
    - trigger: The type of activity (download, search, or web access)
    """
    # First, check if this message contains a "Transition:" marker
    transition_match = re.search(r'Transition: ([A-Z_]+)', message)
    if not transition_match:
        return None

    transition_type = transition_match.group(1)

    # Extract the URL from the message
    url_match = re.search(r'(https?://[^\s]+)', message)
    if not url_match:
        return None

    url = url_match.group(1)
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()
    path = parsed_url.path

    # Case 1: Handle DOWNLOAD transitions
    if transition_type == "DOWNLOAD":
        # Try to extract the filename from parentheses, which is common in browser history
        filename_match = re.search(
            r'\(([^)]+\.(zip|tar\.gz|dmg|exe|deb|msi|pdf|apk|rpm|pkg))\)', message)

        # If we can't find a filename in parentheses, try to extract from the URL path
        if not filename_match:
            # Extract the last component of the path as a potential filename
            path_parts = path.split('/')
            potential_filename = path_parts[-1] if path_parts[-1] else (
                path_parts[-2] if len(path_parts) > 1 else "unknown_file")

            # If there are query parameters, remove them
            potential_filename = potential_filename.split('?')[0]

            state = potential_filename
        else:
            state = filename_match.group(1)

        # Return the filename as state and "downloaded_file" as trigger
        return state, "downloaded_file"

    # Case 2: Handle search queries
    if (netloc.endswith('google.com') or netloc.endswith('bing.com') or
            netloc.endswith('yahoo.com') or netloc.endswith('duckduckgo.com')) and path.startswith('/search'):

        query_params = parse_qs(parsed_url.query)

        # Different search engines use different query parameters
        query_param = None
        search_engine = None

        if 'google.com' in netloc:
            query_param = 'q'
            search_engine = 'google'
        elif 'bing.com' in netloc:
            query_param = 'q'
            search_engine = 'bing'
        elif 'yahoo.com' in netloc:
            query_param = 'p'
            search_engine = 'yahoo'
        elif 'duckduckgo.com' in netloc:
            query_param = 'q'
            search_engine = 'duckduckgo'

        # If we identified a search engine and found a query parameter
        if query_param and query_param in query_params and query_params[query_param]:
            search_query = unquote(
                query_params[query_param][0]).replace('+', ' ')

            # Clean the query to remove special characters
            search_query = re.sub(r'[^\w\s.,?!-]', '', search_query)

            # Return the query as state and engine-specific search trigger
            return search_query, f"performed_{search_engine}_search"

    # Case 3: Handle general web access (LINK, TYPED, REDIRECT, etc.)
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

    # Determine the appropriate trigger based on transition type
    if transition_type == "TYPED":
        return state, "accessed_website_direct"
    elif transition_type == "LINK":
        return state, "accessed_website_link"
    elif transition_type == "REDIRECT_PERMANENT":
        return state, "accessed_website_redirect"
    else:
        return state, "accessed_website"
