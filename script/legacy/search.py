
import re
from urllib.parse import urlparse, parse_qs, unquote


def search_focused_extract(message):
    """
    Extracts web activity information focused on two main categories:
    1. Performing searches: Captures the search query and search engine used
    2. Accessing websites: Captures the domain and up to 3 path segments

    Returns a tuple of (state, trigger) where:
    - state: A string representing the site visited or search performed
    - trigger: Either "accessed_website" or "performed_[engine]_search"
    """
    # Extract the URL from the message
    url_match = re.search(r"(https?://[^\s]+)", message)
    if not url_match:
        # Try to match URLs without protocol
        url_match = re.search(
            r"\b(www\.[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}[^\s]*)", message)
        if not url_match:
            return None
        else:
            # Add http:// prefix if missing
            url = "http://" + url_match.group(1)
    else:
        url = url_match.group(1)

    # Clean the URL by removing trailing punctuation or common non-URL characters
    url = re.sub(r'[.,;:!?)}\]]+$', '', url)

    # Parse the cleaned URL
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()
    query_params = parse_qs(parsed_url.query)
    path = parsed_url.path.lower()

    # Skip processing if the URL is a resource, but print for debugging
    if is_api_or_resource(netloc, path):
        return None

    # Check if this is a search activity
    if is_search_activity(netloc, path, query_params):
        search_query = extract_search_query(netloc, query_params, path)
        search_engine = identify_search_engine(netloc)

        if search_query and search_query != "unknown_query":
            state = f'"{search_query}"'
            # Include the search engine in the trigger
            return state, f"performed_{search_engine}_search"

    # Format the site for general website access
    clean_site = format_site_with_path(netloc, path)
    return clean_site, "accessed_website"


def identify_search_engine(netloc):
    """Identifies which search engine was used."""
    search_engines = {
        'google': ['google.'],
        'bing': ['bing.'],
        'yahoo': ['yahoo.'],
        'duckduckgo': ['duckduckgo.', 'duck.com'],
        'baidu': ['baidu.'],
        'yandex': ['yandex.'],
        'ask': ['ask.'],
        'aol': ['aol.', 'search.aol.'],
        'ecosia': ['ecosia.'],
        'qwant': ['qwant.']
    }

    for engine, domains in search_engines.items():
        if any(domain in netloc for domain in domains):
            return engine

    return "unknown"


def is_api_or_resource(netloc, path):
    """
    Determines if the URL is an API endpoint, CDN resource, or similar non-user-facing URL.
    Returns True if the URL should be excluded from analysis.
    """
    # Exception list - always keep these domains even if they match resource patterns
    exception_domains = [
        'w3schools.com',
        'github.com',
        'stackoverflow.com',
        'docs.python.org'
    ]

    # Check if domain is in exception list
    if any(domain in netloc for domain in exception_domains):
        return False

    # Check file extensions that should be excluded
    resource_extensions = [
        '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff',
        '.woff2', '.ttf', '.eot', '.ico', '.map', '.json', '.xml'
    ]

    if any(path.lower().endswith(ext) for ext in resource_extensions):
        return True

    # Check for domains that are typically resources rather than user-facing
    resource_domains = [
        'cdn.', 'static.', 'assets.', 'img.', 'images.', 'fonts.',
        'analytics.', 'tracking.', 'stats.', 'api.', 'gateway.',
        'r.', 'px.', 's.', 'c.', 'd.', 't.', 'tr.', 'ad.', 'ads.',
        'beacon.', 'metrics.', 'logs.', 'events.'
    ]

    if any(domain in netloc for domain in resource_domains):
        return True

    # Check for resource paths
    resource_paths = [
        '/js/', '/css/', '/img/', '/images/', '/assets/', '/static/',
        '/cdn/', '/api/', '/libs/', '/lib/', '/fonts/', '/icons/',
        '/pixel/', '/tracking/', '/analytics/', '/beacon/', '/metrics/',
        '/rs/', '/rp/', '/rb/'
    ]

    if any(path_segment in path.lower() for path_segment in resource_paths):
        return True

    # Check for common resource filename patterns
    if re.search(r'\.[a-f0-9]{8,}\.', path, re.IGNORECASE):  # Hashed filenames
        return True

    # Check for GUIDs, hashes, or long numeric strings in the path
    if re.search(r'/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', path, re.IGNORECASE) or \
       re.search(r'/[0-9a-f]{32}', path, re.IGNORECASE) or \
       re.search(r'/\d{10,}', path):
        return True

    return False


def is_search_activity(netloc, path, query_params):
    """Determines if the current activity is a search."""
    # Major search engines detection
    search_engines = {
        'google': ['q'],
        'bing': ['q'],
        'yahoo': ['p'],
        'duckduckgo': ['q'],
        'baidu': ['wd', 'word'],
        'yandex': ['text'],
        'ask': ['q'],
        'aol': ['q'],
        'ecosia': ['q'],
        'qwant': ['q']
    }

    for engine, params in search_engines.items():
        if engine in netloc:
            for param in params:
                if param in query_params and query_params[param][0].strip():
                    return True

    # Detect site-specific searches with non-empty query parameters
    if ('search' in path and any(query_params.values())) or \
       any(param in query_params for param in ['q', 'query', 'search', 'keyword', 'term']):
        # Make sure at least one query parameter has a value
        for param in ['q', 'query', 'search', 'keyword', 'term']:
            if param in query_params and query_params[param][0].strip():
                return True

    return False


def extract_search_query(netloc, query_params, path):
    """Extracts the search query based on the search engine."""
    # Different search engines use different query parameter names
    search_engines = {
        'google': ['q'],
        'bing': ['q'],
        'yahoo': ['p'],
        'duckduckgo': ['q'],
        'baidu': ['wd', 'word'],
        'yandex': ['text'],
        'ask': ['q'],
        'aol': ['q'],
        'ecosia': ['q'],
        'qwant': ['q']
    }

    # Add general search parameters for other sites
    search_engines['other'] = ['q', 'query',
                               'search', 'keyword', 'term', 'p', 'text']

    engine = 'other'
    for eng_name in search_engines:
        if eng_name in netloc:
            engine = eng_name
            break

    # Check for the appropriate query parameter
    for param in search_engines[engine]:
        if param in query_params and query_params[param]:
            # Get the query and decode URL encoding
            query = unquote(query_params[param][0]).strip()
            if query:
                # Clean the query but preserve spaces and basic punctuation
                clean_query = re.sub(r'[^\w\s.,?!-]', '', query)
                return clean_query

    return "unknown_query"


def format_site_with_path(netloc, path):
    """
    Formats the site with up to 3 path segments.
    """
    # Clean the netloc to get just the domain
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # Split the path and take up to 3 segments
    path_segments = [segment for segment in path.split('/') if segment]
    path_segments = path_segments[:3]  # Limit to 3 segments

    # Create the formatted site string
    if path_segments:
        return f"{netloc}/{'/'.join(path_segments)}"
    else:
        return netloc
