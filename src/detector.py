"""
detector.py — Core scam-detection logic for ScamCheck.

WEEK 1 GOAL: get check_message() working as a plain Python function you can
call from the terminal. No database, no UI needed yet — just prove the logic
works on real example text.

Each "check_*" function below looks for ONE type of red flag and returns
points + a plain-English reason if it finds something. check_message() runs
all of them and combines the results into a final risk score.
"""

from typing import TypedDict, Optional
import url_utils
import re

class RiskResult(TypedDict):
    score: int            # 0-100, higher = more suspicious
    level: str             # "green" | "yellow" | "red"
    reasons: list[str]     # plain-English explanations for the score


# Score -> level thresholds. Feel free to tune these once you've tested
# against real examples — these are starting points, not fixed rules.

#max level points
GREEN_MAX = 19
YELLOW_MAX = 59

#check points
URGENCY_LANGUAGE_POINT = 5
SENSITIVE_SECURITY_KEYWORD_POINT = 15
SUSPICIOUS_LINK_CAP_POINT = 7
GENERIC_GREETING_POINT = 2
MONEY_REQUEST_POINTS = 8
PRIZE_REWARD_POINTS = 6
THREAT_POINTS = 8
PERSONAL_INFO_POINTS = 8

#combination points
PIN_AND_URGENCY = 20
LINK_AND_URGENCY = 15
LINK_AND_THREAT = 15
MONEY_AND_URGENCY = 15
PERSONAL_INFO_AND_URGENCY = 10


def check_message(text: str) -> RiskResult:
    
    text = text.lower().strip()
    
    total_points = 0
    reasons = []
    
    urgency_points, urgency_reason = check_urgency_language(text)
    total_points += urgency_points
    reasons.append(urgency_reason)
    
    pin_points, pin_reason = check_pin_otp_request(text)
    total_points += pin_points
    reasons.append(pin_reason)
    
    link_points, link_reasons = check_suspicious_links(text)
    total_points += link_points
    reasons.extend(link_reasons)
    
    greeting_points, greeting_reason = check_generic_greeting(text)
    total_points += greeting_points
    reasons.append(greeting_reason)
    
    money_points, money_reason = check_money_request(text)
    total_points += money_points
    reasons.append(money_reason)
    
    prize_points, prize_reason = check_prize_or_reward(text)
    total_points += prize_points
    reasons.append(prize_reason)
    
    threat_points, threat_reason = check_threats_or_consequences(text)
    total_points += threat_points
    reasons.append(threat_reason)
    
    personal_info_points, personal_info_reason = check_personal_information_request(text)
    total_points += personal_info_points
    reasons.append(personal_info_reason)
    
    #combination bonuses
    #didnt use if-elif-else because multiple checks can be true at the same time
    if pin_reason and urgency_reason:
        total_points += PIN_AND_URGENCY
        reasons.append("Urgency combined with a request for sensitive security information.")
    if link_reasons and urgency_reason:
        total_points += LINK_AND_URGENCY
        reasons.append("Urgency combined with a suspicious link.")
    if link_reasons and threat_reason:
        total_points += LINK_AND_THREAT
        reasons.append("A suspicious link is combined with a threat or warning of negative consequences.")
    if money_reason and urgency_reason:
        total_points += MONEY_AND_URGENCY
        reasons.append("An urgent request to send or transfer money.")
    if personal_info_reason and urgency_reason:
        total_points += PERSONAL_INFO_AND_URGENCY
        reasons.append("An urgent request for personal or identifying information.")
    
    total_points = min(total_points, 100)
    reasons = [reason for reason in reasons if reason is not None]#removes None
    
    if total_points <= GREEN_MAX:
        level = "GREEN"
    elif total_points <= YELLOW_MAX:
        level = "YELLOW"
    else:
        level = "RED"
        
    riskResult: RiskResult = {
        "score" : total_points,
        "level" : level,
        "reasons" : reasons        
        }    
    
    return riskResult

def check_urgency_language(text: str) -> tuple[int, Optional[str]]:
    
    urgency_phrases = urgency_phrases = [  #Add More
    "act now",
    "act immediately",
    "account will be blocked",
    "account will be suspended",
    "immediately",
    "within 24 hours",
    "within 48 hours",
    "urgent action required",
    "urgent response required",
    "respond immediately",
    ]
    
    total_points = 0
    reason_string = None
    urgency_phrases_detected = []
    
    for urgency_phrase in urgency_phrases:
        if re.search(rf"\b{re.escape(urgency_phrase)}\b", text):
            total_points += URGENCY_LANGUAGE_POINT
            urgency_phrases_detected.append(urgency_phrase)            
    
    if urgency_phrases_detected:
        phrases_str = ", ".join([f"'{phrase}'" for phrase in urgency_phrases_detected])
        reason_string = f"Urgency Phrase Detected: {phrases_str}"           
        
    return (total_points, reason_string)


def check_pin_otp_request(text: str) -> tuple[int, Optional[str]]:
    sensitive_keywords = [#add more
    "pin",
    "otp",
    "password",
    "passcode",
    "cvv",
    "security code",
    "verification code",
    "account details",
    "login details",
    "nin",
    "bvn"
    ]
    
    total_points = 0
    reason_string = None
    sensitive_keywords_detected = [] 
    
    for keyword in sensitive_keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            total_points += SENSITIVE_SECURITY_KEYWORD_POINT
            sensitive_keywords_detected.append(keyword)
            
    if sensitive_keywords_detected:
        phrases_str = ", ".join([f"'{phrase}'" for phrase in sensitive_keywords_detected])
        reason_string = f"Sensitive Keyword Request Detected: {phrases_str}"
    return (total_points, reason_string)


def check_suspicious_links(text: str) -> tuple[int, list[str]]:
    """
    Look for URLs in the text, especially ones that:
    
        Uses a shortened URL — e.g. bit.ly, tinyurl.com                                     +2
        Uses an IP address instead of a domain name                                         +2
        Possible bank lookalike domain — e.g. gtbank-secure-verify.com                      +3
        Contains suspicious security/account language — e.g. login, verify, account, etc.   +1
        Contains misleading @ structure — e.g. trusted-site.com@192.168.1.10                +3
        Uses a Punycode domain — hostname contains xn--                                     +1
        Contains excessive percent-encoding — 3+ %XX sequences anywhere in the URL          +1
    """
    
    total_points = 0
    total_reasons_list = []
    break_down = []
    
    url_list = url_utils.url_extractor(text)    
    
    
    for url in url_list:
        url_points = 0
        url_reasons_list = []
    
        points, reason_string = url_utils.check_shortened_link(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_ipaddress(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_valid_bank_url(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_suspicious_language(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_url_structure(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_punycode_domain(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_excessive_percent_encoding(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        # NEW: catches links hosted on legitimate platforms (e.g. cloud
        # storage) that domain-reputation checks above can't flag, because
        # the giveaway is in the path/fragment or query string shape, not
        # the domain itself. Added after the False Negative test cases
        # (storage.googleapis.com links) were found to score 0 otherwise.
        points, reason_string = url_utils.check_suspicious_path(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        points, reason_string = url_utils.check_redirect_parameters(url)
        url_points += points
        url_reasons_list.append(reason_string)

        points, reason_string = url_utils.check_malformed_query(url)
        url_points += points
        url_reasons_list.append(reason_string)
        
        url_reasons_list = [reason for reason in url_reasons_list if reason is not None] #Removes None
        
        capped_url_points = min(url_points, SUSPICIOUS_LINK_CAP_POINT) #cap individual url points at 7
        total_points += capped_url_points
        total_reasons_list.extend(url_reasons_list)
        
        break_down.append({"URL" : url, "Points" : url_points, "Reasons" : url_reasons_list})        
        
    return (total_points, total_reasons_list)


def check_generic_greeting(text: str) -> tuple[int, Optional[str]]:
    
    generic_greetings = [#add more
        "dear customer",
        "dear valued customer",
        "dear account holder"
    ]
    
    total_points = 0
    reason_string = None
    generic_greetings_detected = []
    
    for greeting in generic_greetings:
        if re.search(rf"\b{re.escape(greeting)}\b", text):
            total_points += GENERIC_GREETING_POINT
            generic_greetings_detected.append(greeting)
            
    if generic_greetings_detected:
        phrases_str = ", ".join([f"'{phrase}'" for phrase in generic_greetings_detected])
        reason_string = f"Generic Greeting Detected: {phrases_str}"
    return (total_points, reason_string)

#Added check_* functions
#check_money_request()
#check_prize_or_reward()
#check_threats_or_consequences()
#check_personal_information_request()

def check_money_request(text: str) -> tuple[int, Optional[str]]:
    
    points = 0
    reason_string = None
    
    money_request_phrases = [
    "send money",
    "send funds",
    "send payment",
    "make a payment",
    "make payment",
    "transfer money",
    "transfer funds",
    "make a transfer",
    "pay now",
    "pay immediately",
    "pay the fee",
    "pay the charge",
    "pay the amount",
    "pay the balance",
    "send the amount",
    "transfer the amount",
    "deposit money",
    "deposit funds",
    "send to this account",
    "transfer to this account",
    ]
    
    for phrase in money_request_phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", text):
            points += MONEY_REQUEST_POINTS
            reason_string = "The message asks you to send, transfer, or pay money."
        
    return (points, reason_string)

def check_prize_or_reward(text: str) -> tuple[int, Optional[str]]:
    
    points = 0
    reason_string = None
    
    prize_reward_phrases = [
    "you have won",
    "you've won",
    "you are a winner",
    "you've been selected",
    "you have been selected",
    "congratulations, you have won",
    "claim your prize",
    "claim your reward",
    "claim your winnings",
    "collect your prize",
    "collect your reward",
    "lottery winner",
    "lottery prize",
    "cash prize",
    "cash reward",
    "you won a prize",
    "you won a reward",
    "exclusive reward",
    "special reward",
    "free gift",
    ]
    
    for phrase in prize_reward_phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", text):
            points += PRIZE_REWARD_POINTS
            reason_string = "The message claims you have won a prize or reward."
    
    return (points, reason_string)

def check_threats_or_consequences(text: str) -> tuple[int, Optional[str]]:
    
    points = 0
    reason_string = None
    
    threat_phrases = [
    "legal action",
    "legal proceedings",
    "court action",
    "arrest warrant",
    "you will be arrested",
    "you may be arrested",
    "account will be closed",
    "account will be suspended",
    "account will be blocked",
    "access will be revoked",
    "you will lose access",
    "service will be terminated",
    "service will be suspended",
    "you will be fined",
    "a penalty will apply",
    "penalty will be charged",
    "failure to comply",
    "failure to respond",
    ]
    
    for phrase in threat_phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", text):
            points += THREAT_POINTS
            reason_string = "The message contains threats or warnings about negative consequences."
            
    return (points, reason_string)

def check_personal_information_request(text: str) -> tuple[int, Optional[str]]:
    
    points = 0
    reason_string = None
    
    personal_info_phrases = [
    "date of birth",
    "home address",
    "residential address",
    "id number",
    "identification number",
    "national id",
    "identity card",
    "passport number",
    "driver's license",
    "social security number",
    "bank account number",
    ]
    
    for phrase in personal_info_phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", text):
            points += PERSONAL_INFO_POINTS
            reason_string = "The message asks for personal or identifying information."
            
    return (points, reason_string)    
        
if __name__ == "__main__":
    test_messages = [
        "Dear Customer, your account will be blocked in 24 hours. Click here to verify: http://gtb-secure-verify.com",        
        "Hi Chidi, your OPay wallet statement for July is ready to view.",        
        "URGENT: Your BVN has been suspended. Send your PIN and OTP to this number immediately to reactivate.",
    ]
    
    added_test_messages = [
        "Please respond immediately to this message.",
        "Send your OTP to verify your account.",
        "Click here to claim your reward: [link]",
        "Your account will be suspended if you do not respond." ,
        "URGENT: Your account will be suspended today. Send your OTP and password immediately to avoid permanent closure."
    ]
    
    added_test_messages_2 = [
        "Hi Chidi, your OPay wallet statement for July is ready to view.",
        "Please respond immediately to confirm your appointment for tomorrow.",
        "Your electricity bill is due tomorrow. Please make your payment through the official app.",
        "Please provide your date of birth to complete your registration.",
        "Congratulations, you have won a cash prize. Claim your reward today.",
        "Dear Customer, please respond immediately to this message.",
        "Your account will be suspended if you do not respond within 24 hours.",
        "URGENT: Send your OTP immediately to prevent your account from being blocked.",
        "Dear Customer, your account will be blocked today. Verify immediately at http://gtb-secure-verify.com",
        "URGENT: Your account will be permanently suspended. Send your OTP, PIN and password immediately, or legal action will be taken. Pay the verification fee at http://secure-gtb-verify.com",
        "",
        ""
    ]
    
    for msg in test_messages:
        print("-" * 60)
        print(f"Message: {msg}")
        result = check_message(msg)
        print(f"Result: {result}")

