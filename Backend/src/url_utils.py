from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs
import re
import math
import ipaddress
from collections import Counter
from urlextract import URLExtract
import tldextract
import unicodedata
import datetime
import whois
import requests

# Format: "brand_keyword": ["primary_domain.com", "alternate_domain.com"]
PROTECTED_BANKS = {
    "accessbank": ["accessbankplc.com"],
    "access": ["accessbankplc.com"],
    
    "gtbank": ["gtbank.com"],
    "gtb": ["gtbank.com"],
    
    "zenith": ["zenithbank.com", "zenithbank.com.ng"],
    
    "firstbank": ["firstbanknigeria.com"],
    
    "uba": ["ubagroup.com"],
    
    "opay": ["opayweb.com"],
    
    "kuda": ["kuda.com"],
    
    "moniepoint": ["moniepoint.com"],
    
    "sterling": ["sterling.ng"],
    
    "wema": ["wemabank.com"],
    
    "fidelity": ["fidelitybank.ng"],
    
    "unionbank": ["unionbankng.com"],
    
    "stanbic": ["stanbicibtcbank.com"],
    
    "polaris": ["polarisbanklimited.com"],
    
    "fcmb": ["fcmb.com"],
}


def url_extractor_basic(text: str) -> list[str]:
    pattern =  r'(?<![@\w.-])(?:https?://\S+|www\.\S+|(?:[\w-]+\.)+[a-zA-Z]{2,}(?:/\s*)?)'
    urls = [url.rstrip(".,!?;:)]}") for url in re.findall(pattern, text)]
    return urls



def url_extractor(text: str) -> list[str]:
    extractor = URLExtract()
    extractor.permit_ips = True         # Detect 127.0.0.1, 192.168.1.1, etc.
    extractor.permit_unicode = True      # Full Internationalized Domain Name (IDN) support (e.g., münchen.de)



    # Standard non-web payload schemes that don't use domain TLDs

    PAYLOAD_SCHEMES = ('javascript:', 'data:', 'vbscript:', 'file:', 'view-source:')
    PAYLOAD_PATTERN = r'(?<![@\w.-])(?:javascript|data|vbscript|file|view-source):\S+'
    
    raw_candidates = []

    # 1. Extract non-web payload schemes (since urlextract only targets domain-based links)

    for match in re.finditer(PAYLOAD_PATTERN, text, re.IGNORECASE):
        raw_candidates.append(match.group(0))
        
    # 2. Extract standard web URLs, IP addresses, and Unicode domains using URLExtract

    web_urls = extractor.find_urls(text, check_dns=False)
    raw_candidates.extend(web_urls)



    # 3. Uniform Cleaning & Validation

    cleaned_urls = []    

    # Trailing noise characters across markdown, code, and text formatting

    TRAILING_NOISE = ".,!?;:'\"<>|{}[]"

    for url in raw_candidates:
        cleaned = url
        url_lower = cleaned.lower()



        # Payload handling

        if url_lower.startswith(PAYLOAD_SCHEMES):
            # For data: URIs, preserve inner characters; only trim trailing prose noise

            if not url_lower.startswith('data:'):
                cleaned = cleaned.rstrip(TRAILING_NOISE)
            else:
                cleaned = cleaned.rstrip(",!?;:'\"<>|{}[]")
            cleaned_urls.append(cleaned)
            continue



        # Standard Web URL cleanup

        cleaned = cleaned.rstrip(TRAILING_NOISE)

        # Balance trailing parentheses (e.g. Wikipedia: .../Function_(mathematics))

        if cleaned.endswith(')') and cleaned.count('(') < cleaned.count(')'):
            cleaned = cleaned[:-1]

        # Validate structure via tldextract or explicit scheme check

        ext = tldextract.extract(cleaned)
        is_valid_web = bool(
            (ext.domain and ext.suffix) or 
            ext.ipv4 or 
            ext.ipv6 or 
            cleaned.lower().startswith(('http://', 'https://', 'ftp://'))
        )



        if is_valid_web:
            cleaned_urls.append(cleaned)

    # 4. Deduplicate and remove substring fragments

    final_urls = []
    for url in cleaned_urls:
        # If a candidate is just a sub-fragment of a larger valid URL captured in the same pass, ignore it

        if any(url != longer and url in longer for longer in cleaned_urls):
            continue
        if url not in final_urls:
            final_urls.append(url)

    return final_urls


def parse_url_safely(url: str) -> Tuple[bool, str]:
    """
    Attempts to parse a URL safely using urllib.parse.urlparse.
    """
    
    try:
        parsed = urlparse(url)
        return True, "URL parsed successfully"
    except Exception as e:
        return False, f"Malformed URL structure: {str(e)}"

def check_scheme_safety(url: str) -> Tuple[bool, int, str]:
    """Ensure the URL explicitly uses http or https."""
    parsed_url = urlparse(url)
    scheme = (parsed_url.scheme or "").lower().strip()
    
    # Case 1: Missing scheme (e.g. "google.com" passed without "https://")
    if not scheme:
        return False, 0, "Missing scheme (http:// or https:// required)"
    
    # Case 2: Non-web or dangerous URI schemes (e.g. javascript:, file://, data:)
    if scheme not in ("http", "https"):
        return False, 7, f"Unsupported or dangerous scheme: '{scheme}:'"
    
    return True, 0, "Scheme is valid (http/https)"

def check_hostname(url: str) -> Tuple[bool, int, str]:
    parsed_url = urlparse(url)
    if not parsed_url.hostname:
        return False, 0, 'Missing destination host/domain'

    return (True, 0, 'Hostname is present')

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
    points = 0
    reason_string = None
    
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    username = parsed_url.username
    
    # Check hostname normally, but treat ANY bank identifier in the username field as a fake lookalike
    if looks_like_bank(hostname, PROTECTED_BANKS) or looks_like_bank(username, PROTECTED_BANKS, is_username=True):
        points = BANK_LOOKALIKE_POINTS
        reason_string = "Possible bank lookalike domain"
        
    return (points, reason_string)


def looks_like_bank(candidate: str | None, banks: dict[str, list[str]], is_username: bool = False) -> bool:
    if candidate is None:
        return False
        
    candidate = candidate.lower().rstrip(".")
    
    for bank_name, official_domains in banks.items():
        if bank_name in candidate:
            # If the bank name appears in the username field (e.g. gtbank.com@evil.com), 
            # it is ALWAYS suspicious obfuscation
            if is_username:
                return True

            # For hostnames, verify if it's an official domain or subdomain
            is_legitimate = any(
                candidate == official_domain or candidate.endswith("." + official_domain)
                for official_domain in official_domains
            )
            
            if not is_legitimate:
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
    LONG_SEGMENT_THRESHOLD = 25  # characters
    ENTROPY_THRESHOLD = 3.8      # bits/char — ordinary words score lower than this

    points = 0
    reason_string = None

    parsed_url = urlparse(url)

    segments = []
    if parsed_url.path:
        segments.extend(seg for seg in parsed_url.path.split('/') if seg)
    if parsed_url.fragment:
        # the fragment can itself contain path-like or query-like structure
        segments.extend(seg for seg in re.split(r'[/&?]', parsed_url.fragment) if seg)

    for segment in segments:
        clean_segment = segment.split('?')[0].rsplit('.', 1)[0]  # Strip query string off segment and strip only the trailing file extension
        
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

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # some redirect chains hide their params after '#...?...' instead of
    # in the real query string
    if '?' in parsed_url.fragment:
        query_params.update(parse_qs(parsed_url.fragment.split('?', 1)[1]))

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


def check_malformed_query(url: str) -> Tuple[int, Optional[str]]:
    """
    Flags query strings that contain a value/token but no key=value
    structure, e.g.:

        http://example.com/index.php?8b9sol

    This can indicate a malformed or suspicious URL generated by
    a compromised website or malicious redirect.
    """
    MALFORMED_QUERY_POINTS = 2
    
    points = 0
    reason_string = None

    parsed_url = urlparse(url)

    if parsed_url.query and "=" not in parsed_url.query:
        if not parsed_url.query.strip().isdigit():
            points = MALFORMED_QUERY_POINTS
            reason_string = "Contains a malformed or suspicious query string"
            return (points, reason_string)

    return (points, reason_string)

def check_typosquatting(url: str) -> Tuple[int, Optional[str]]:
    """
    Detects typosquatting, character swaps, brand keyword appending,
    and subdomain spoofing against protected financial institutions.
    """
    TYPOSQUATTING_POINTS = 3

    check_url = url if "://" in url else "http://" + url
    parsed = urlparse(check_url)
    hostname = (parsed.hostname or "").lower()

    if not hostname:
        return (0, None)

    ext = tldextract.extract(hostname)
    domain_name = ext.domain.lower()
    subdomain = ext.subdomain.lower()
    registered_domain = ext.top_domain_under_public_suffix.lower()

    if not domain_name:
        return (0, None)

    # 1. Decode Punycode & normalize Unicode accents (e.g. k̇da -> kuda)
    decoded_domain = domain_name
    if domain_name.startswith("xn--"):
        try:
            raw_decoded = domain_name.encode("ascii").decode("idna").lower()
            normalized = unicodedata.normalize("NFKD", raw_decoded)
            decoded_domain = "".join(c for c in normalized if not unicodedata.combining(c))
        except Exception:
            decoded_domain = domain_name

    # Clean domain string without hyphens/underscores for character checks
    cleaned_domain_str = decoded_domain.replace("_", "").replace("-", "")

    # 2. Extract official registered domains and official base brand names (e.g., 'gtbank', 'fidelitybank')
    all_official_domains = set()
    official_base_names = set()

    for domains_list in PROTECTED_BANKS.values():
        for d in domains_list:
            d_lower = d.lower()
            all_official_domains.add(d_lower)
            ext_d = tldextract.extract(d_lower)
            if ext_d.domain:
                official_base_names.add(ext_d.domain.lower())

    # --- STAGE 1: HARD WHITELIST CHECK ---
    # Exact match for official domain or legitimate official subdomain
    if registered_domain in all_official_domains or any(hostname.endswith("." + d) for d in all_official_domains):
        return (0, None)

    # --- STAGE 2: LEVENSHTEIN / TYPOSQUATTING CHECK ---
    # Compare extracted domain directly against official base names (e.g., 'gtbank', 'fidelitybank', 'kuda')
    for official_name in official_base_names:
        distance = _levenshtein_distance(cleaned_domain_str, official_name)

        # Allow 1 edit for short brands (<=5 chars), 2 edits for longer brands (>5 chars)
        max_allowed_distance = 1 if len(official_name) <= 5 else 2

        if 0 < distance <= max_allowed_distance:
            return (TYPOSQUATTING_POINTS, f"Possible typosquatting lookalike of protected domain ({official_name})")

    # --- STAGE 3: BRAND SPOOFING & KEYWORD COMBINATIONS ---
    SUSPICIOUS_WORDS = (
        "bank", "login", "verify", "secure", "security", "portal", "update", "upgrade",
        "account", "online", "support", "service", "agent", "app", "alat"
    )

    # Check if a protected brand keyword appears in subdomain or domain string
    for brand_key in PROTECTED_BANKS.keys():
        clean_key = brand_key.replace(" ", "").lower()
        if len(clean_key) < 3:
            continue

        # A) Brand keyword in Subdomain (e.g., accessbank.support-portal.net)
        if clean_key in subdomain:
            return (TYPOSQUATTING_POINTS, f"Protected brand keyword ({clean_key}) used in subdomain")

        # B) Brand keyword combined with hyphens/underscores/suspicious words (e.g., gt_bank_security, wema-alat-upgrade)
        if clean_key in cleaned_domain_str:
            has_delimiters = "-" in domain_name or "_" in domain_name
            has_security_words = any(w in domain_name for w in SUSPICIOUS_WORDS)
            
            # Exact brand name on unapproved TLD (e.g., wemabank.net)
            if decoded_domain in official_base_names:
                return (TYPOSQUATTING_POINTS, f"Official brand name ({decoded_domain}) registered on untrusted TLD")

            if has_delimiters or has_security_words:
                return (TYPOSQUATTING_POINTS, f"Protected brand keyword ({clean_key}) used with suspicious context")

    return (0, None)


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Computes the Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def check_domain_age(url: str) -> Tuple[int, Optional[str]]:
    """
    Queries WHOIS data to determine the domain's age.
    Identifies brand-new or freshly registered domains.
    Cybercriminals rely on Newly Registered Domains
    (NRDs)—specifically domains less than 30 days old—because
    they exploit a fundamental weakness in internet security: the "Clean Slate" advantage.
    """
    
    try:
        cleaned_input = url.strip()
        if not cleaned_input.startswith(("http://", "https://")):
            cleaned_input = "http://" + cleaned_input

        parsed = urlparse(cleaned_input)
        domain = parsed.hostname or ""

        if domain.startswith("www."):
            domain = domain[4:]

        if not domain:
            return (0, None)
        
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        # 1. Extract first element if WHOIS returns a list
        if isinstance(creation_date, list) and len(creation_date) > 0:
            creation_date = creation_date[0]

        if not creation_date:
            return (0, None)

        # 2. Convert string responses to datetime objects
        if isinstance(creation_date, str):
            # Clean common ISO and standard string formats
            clean_str = creation_date.split("T")[0].split(" ")[0]
            try:
                creation_date = datetime.datetime.strptime(clean_str, "%Y-%m-%d")
            except ValueError:
                return (0, None)

        # 3. Handle datetime objects & strip timezone offsets
        if isinstance(creation_date, datetime.datetime):
            creation_date = creation_date.date()
            
        if isinstance(creation_date, datetime.date):
            today = datetime.date.today()
            age_days = (today - creation_date).days

            if age_days < 30:
                return (3, f"Newly registered domain (Only {age_days} days old)")
            elif age_days < 90:
                return (2, f"Recently registered domain ({age_days} days old)")

    except Exception:
        # Handles connection timeouts, redacted privacy fields, or dead domains
        pass

    return (0, None)

def check_google_safe_browsing(url: str, api_key: str = "AIzaSyCSyuB6P3SsW20mfzrBPhNNPu93Gc_P0io") -> Tuple[int, Optional[str]]:#Identifies already-reported active phishing, malware, or scam links.
    """
    Queries Google Safe Browsing API v4 for real-time phishing/malware status.
    """
    if not api_key:
        return (0, None)

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {
            "clientId": "ScamCheck-Pipeline",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=3.0)
        if response.status_code == 200:
            data = response.json()
            if "matches" in data and len(data["matches"]) > 0:
                threat_type = data["matches"][0].get("threatType", "PHISHING")
                return (5, f"Flagged by Google Safe Browsing ({threat_type})")
    except requests.exceptions.RequestException:
        pass
        

    return (0, None)