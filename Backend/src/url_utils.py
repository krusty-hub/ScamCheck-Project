from typing import Optional
from urllib.parse import urlparse, parse_qs
import re
import math
import ipaddress
from collections import Counter

def url_extractor(text: str) -> list[str]:
    pattern =  r'(?<![@\w.-])(?:https?://\S+|www\.\S+|(?:[\w-]+\.)+[a-zA-Z]{2,}(?:/\s*)?)'
    urls = [url.rstrip(".,!?;:)]}") for url in re.findall(pattern, text)]
    return urls

def check_shortened_link(url: str) -> tuple[int, Optional[str]]:
    SHORTENED_URL_POINTS = 2
    points = 0
    reason_string = None
    
    
    hostname = urlparse(url).hostname #extracts the domain name
    
    shortened_domains = ["bit.ly", "tinyurl.com", "t.co"]
    
    if hostname in shortened_domains:
        points = SHORTENED_URL_POINTS
        reason_string = "Uses a URL Shortening Service"
        
    return (points, reason_string)

def check_ipaddress(url: str) -> tuple[int, Optional[str]]:
    IP_ADDRESS_POINTS = 2
    points = 0
    reason_string = None
    
    hostname = urlparse(url).hostname
    
    if hostname is not None:
        try:
            ipaddress.ip_address(hostname)#checks whether the domain is a valid ip address
            points = IP_ADDRESS_POINTS
            reason_string = "Uses an IP Address instead of a Domain Name"
        except ValueError:
            pass
    
    return (points, reason_string)

def check_valid_bank_url(url: str) -> tuple[int, Optional[str]]:
    BANK_LOOKALIKE_POINTS = 3

    # Bank identifiers mapped to their official domains.
    # Add new banks here as the project expands.
    banks = {
        "accessbank": ["accessbankplc.com"],
        "access": ["accessbankplc.com"],

        "gtbank": ["gtbank.com"],
        "gtb": ["gtbank.com"],

        "zenith": ["zenithbank.com"],

        "firstbank": ["firstbanknigeria.com"],
        "first bank": ["firstbanknigeria.com"],

        "uba": ["ubagroup.com"],

        "opay": ["opayweb.com"],

        "kuda": ["kuda.com"],

        "moniepoint": ["moniepoint.com"],

        "sterling": ["sterling.ng"],

        "wema": ["wemabank.com"],

        "fidelity": ["fidelitybank.ng"],

        "unionbank": ["unionbankng.com"],
        "union bank": ["unionbankng.com"],

        "stanbic": ["stanbicibtcbank.com"],

        "polaris": ["polarisbanklimited.com"],

        "fcmb": ["fcmb.com"],
    }

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    # No hostname means there is no domain to inspect.
    if hostname is None:
        return (0, None)

    hostname = hostname.lower().rstrip(".")

    if looks_like_bank(hostname, banks):
        return (
            BANK_LOOKALIKE_POINTS,
            "Possible bank lookalike domain"
        )

    return (0, None)


def looks_like_bank(
    hostname: str,
    banks: dict[str, list[str]]
) -> bool:
    hostname = hostname.lower()

    for bank_name, official_domains in banks.items():

        # Does the hostname contain a bank identifier?
        if bank_name in hostname:

            # Check whether it is an official domain or subdomain
            for official_domain in official_domains:

                if (
                    hostname == official_domain
                    or hostname.endswith("." + official_domain)
                ):
                    return False

            # It mentions the bank but is not an official domain.
            return True

    return False
                
                
def check_suspicious_language(url: str) -> tuple[int, Optional[str]]:
    SUSPICIOUS_LANGUAGE_POINTS = 1
    points = 0
    reason_string = None
    
    suspicious_keywords = ["login", "verify", "verification", "security", "account", "update"]
    
    path = urlparse(url).path
    
    for keyword in suspicious_keywords:
        if keyword in path:
            points = SUSPICIOUS_LANGUAGE_POINTS
            reason_string = "Contains Suspicious security or account-related languages"
            
    return (points, reason_string)

def check_url_structure(url: str) -> tuple[int, Optional[str]]:
    MISLEADING_AT_POINTS = 3
    points = 0
    reason_string = None
    
    username = urlparse(url).username
    
    if username is not None:
        points = MISLEADING_AT_POINTS
        reason_string = "Contains Misleading @ Structure"
    
    return (points, reason_string)

def check_punycode_domain(url: str) -> tuple[int, Optional[str]]:
    PUNYCODE_DOMAIN_POINTS = 1
    points = 0
    reason_string = None
    
    hostname = urlparse(url).hostname
    
    if hostname is not None and "xn--" in hostname:
        points = PUNYCODE_DOMAIN_POINTS
        reason_string = "Uses a Punycode domain"
        
    return (points, reason_string)

def check_excessive_percent_encoding(url: str) -> tuple[int, Optional[str]]:
    EXCESSIVE_PERCENT_ENCODING_POINTS = 1
    points = 0
    reason_string = None
    
    pattern = re.findall(r'%[0-9a-fA-F]{2}', url)
    
    if len(pattern) >= 3:
        points = EXCESSIVE_PERCENT_ENCODING_POINTS 
        reason_string = "Contains Excessive URL Encoding"
      
    return (points, reason_string)


# --- NEW: added to catch the False Negative cases found during demo testing ---
# Those cases (storage.googleapis.com links) all shared one thing in common:
# the DOMAIN was legitimate (a real Google service), so every check above
# correctly found nothing wrong with it. What gave them away instead was the
# PATH/FRAGMENT and QUERY STRING shape — the parts scammers actually control
# when they abuse a trusted platform to host something malicious.

def _shannon_entropy(s: str) -> float:
    """
    Measures how "random-looking" a string is, in bits per character.
    Ordinary words/filenames score low (predictable letter patterns).
    Randomly-generated strings score high (every character is a near-even
    surprise). This is the same idea used in real-world spam/phishing
    filters to spot auto-generated tokens.
    """
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def check_suspicious_path(url: str) -> tuple[int, Optional[str]]:
    """
    Flags long, high-entropy (random-looking) segments in the URL's path
    or fragment (the part after '#').

    Why this matters: a legitimate page's path usually reads like words —
    /login, /account/settings, /flores.html. A link built to evade
    blocklists and guessing often uses a long, random-looking token instead,
    e.g.:
        /cocodrillo/thannina.html#4tpVAP86551fyrC701bwwrzwwqje18504...

    We check the fragment as well as the path because scammers sometimes
    put the "payload" identifier after the '#' specifically because that
    part is never sent to the server — only read by client-side scripts —
    so it's invisible to simple server-side link scanners.
    """
    SUSPICIOUS_PATH_POINTS = 3
    LONG_SEGMENT_THRESHOLD = 20   # characters
    ENTROPY_THRESHOLD = 3.5       # bits/char — ordinary words score lower than this

    points = 0
    reason_string = None

    parsed = urlparse(url)

    segments = []
    if parsed.path:
        segments.extend(seg for seg in parsed.path.split('/') if seg)
    if parsed.fragment:
        # the fragment can itself contain path-like or query-like structure
        segments.extend(seg for seg in re.split(r'[/&?]', parsed.fragment) if seg)

    for segment in segments:
        clean_segment = segment.split('.')[0]  # ignore file extensions like .html
        if len(clean_segment) >= LONG_SEGMENT_THRESHOLD:
            entropy = _shannon_entropy(clean_segment)
            if entropy >= ENTROPY_THRESHOLD:
                points = SUSPICIOUS_PATH_POINTS
                reason_string = "Contains a long, random-looking path or fragment"
                break

    return (points, reason_string)


def check_redirect_parameters(url: str) -> tuple[int, Optional[str]]:
    """
    Flags query strings shaped like ad-tracking / click-redirect chains,
    e.g.:
        ?act=cl&pid=10638_md&uid=2&vid=257909&ofid=335&lid=420&cid=360745

    We deliberately do NOT hardcode these exact parameter names — scammers
    will just rename them next time. Instead we look at the SHAPE of the
    query string: several short parameter names, most of them holding
    plain numeric (or numeric + short suffix) values. A real, human-facing
    page rarely needs 4+ numeric tracking IDs just to load — that pattern
    is much more typical of a redirect/tracking hop on the way to a final
    (often malicious) destination.

    Also checks the fragment for a "?key=value" style query, since some
    redirect chains put their parameters there instead of the real query
    string (this is what FN04 in the False Negative test cases does).
    """
    REDIRECT_PATTERN_POINTS = 3
    MIN_PARAM_COUNT = 4
    NUMERIC_VALUE_RATIO_THRESHOLD = 0.6  # 60%+ of param values look numeric

    points = 0
    reason_string = None

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    # some redirect chains hide their params after '#...?...' instead of
    # in the real query string
    if '?' in parsed.fragment:
        query_params.update(parse_qs(parsed.fragment.split('?', 1)[1]))

    if len(query_params) >= MIN_PARAM_COUNT:
        numeric_like = 0
        for values in query_params.values():
            value = values[0] if values else ""
            # matches "10638", "2", "10638_md" — numeric, optionally with
            # a short trailing tag
            if re.match(r'^\d+(_\w+)?$', value):
                numeric_like += 1

        if numeric_like / len(query_params) >= NUMERIC_VALUE_RATIO_THRESHOLD:
            points = REDIRECT_PATTERN_POINTS
            reason_string = "Contains ad-redirect/click-tracking style query parameters"

    return (points, reason_string)


def check_malformed_query(url: str) -> tuple[int, Optional[str]]:
    """
    Flags query strings that contain a value/token but no key=value
    structure, e.g.:

        http://example.com/index.php?8b9sol

    This can indicate a malformed or suspicious URL generated by
    a compromised website or malicious redirect.
    """
    MALFORMED_QUERY_POINTS = 2

    parsed = urlparse(url)

    if parsed.query and "=" not in parsed.query:
        return (
            MALFORMED_QUERY_POINTS,
            "Contains a malformed or suspicious query string"
        )

    return (0, None)
