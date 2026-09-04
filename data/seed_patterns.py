"""
seed_patterns.py — Starter scam examples/patterns for ScamCheck.

WEEK 2 GOAL: expand this list to at least 15-20 real scam examples/patterns,
then move it into SQLite (see src/db.py).

Each entry is a real-world-style example with a label so you can use these
both as test cases for your detector AND as seed rows for your database.
Look at real scam SMS/emails you've seen (or search for common Nigerian bank
scam examples) for inspiration — the more realistic, the better your demo.
"""

# A few starter examples to get you going — ADD MORE.
SEED_EXAMPLES = [
    {
        "text": "Dear Customer, your account will be blocked in 24 hours. Click here to verify: http://gtb-secure-verify.com",
        "label": "scam",
        "notes": "Urgency + generic greeting + lookalike domain",
    },
    {
        "text": "URGENT: Your BVN has been suspended. Send your PIN and OTP to this number immediately to reactivate.",
        "label": "scam",
        "notes": "Urgency + direct PIN/OTP request (classic pattern)",
    },
    {
        "text": "Hi Chidi, your OPay wallet statement for July is ready to view in the app.",
        "label": "safe",
        "notes": "Personalized, no urgency, no link/PIN request",
    },
    {
        "text": "CONGRATULATIONS! You have won N500,000 in the MTN promo. Send your account number and PIN to claim.",
        "label": "scam",
        "notes": "Prize/lottery scam + PIN request",
    },
    {
        "text": "Your delivery is on its way and will arrive between 2-4pm today. Reply STOP to opt out of updates.",
        "label": "safe",
        "notes": "Everyday transactional message, no red flags",
    },
    {
        "text": "Your Netflix subscription could not be renewed. Update your payment details at http://netflix-billing-check.com to avoid interruption.",
        "label": "scam",
        "notes": "Suspicious lookalike URL + payment/account pressure"
        },
    {        
        "text": "You have been selected for a special cash reward. Pay a ₦2,500 processing fee to receive your prize.",
        "label": "scam",
        "notes": "Prize/reward claim + money request"
        },
    {        
        "text": "Your electricity account is overdue. Please make payment through the official provider app before the due date.",
        "label": "safe",
        "notes": "Normal billing/payment reminder"
        },
    {        
        "text": "Your bank statement for August is now available. Log in through your usual banking app to view it.",
        "label": "safe",
        "notes": "Routine account notification"
        },
    {        
        "text": "Your parcel is ready for collection at our Ikeja pickup centre. Bring a valid ID when collecting it.",
        "label": "safe",
        "notes": "Normal delivery notification"
        },
    {        
        "text": "Your account will be permanently suspended unless you verify your identity immediately by sending your NIN and date of birth.",
        "label": "scam",
        "notes": "Threat + urgency + personal-information request"
        },
    {        
        "text": "Please provide your date of birth and identification number to complete your university registration.",
        "label": "safe",
        "notes": "Reasonable personal-information request in a registration context"
        },
    {        
        "text": "URGENT: Your payment has failed. Transfer ₦15,000 to the account below within 2 hours or your service will be terminated.",
        "label": "scam",
        "notes": "Urgency + money request + threat"
        },
    {
        "text": "Your password expires in 7 days. Please update it through the official website to maintain access to your account.",
        "label": "safe",
        "notes": "Normal security reminder"
        },
    {
        "text": "Your reward is waiting! Claim your exclusive gift now at http://claim-your-reward-now.com before the offer expires.",
        "label": "scam",
        "notes": "Prize/reward language + suspicious URL + urgency"
        }
    # TODO: add 10-15 more. Try to include a mix of:
    #   - scam examples with different tactics (fake job offers, romance
    #     scams, fake customer care numbers, phishing links, fake refunds)
    #   - safe/legitimate examples that might otherwise look suspicious
    #     (these matter just as much — your detector needs to NOT flag them)
]

def run_extractor_tests_ai():
    test_cases = [
        # -------------------------------------------------------------------------
        # 1. Standard Web Links & Domain Formats
        # -------------------------------------------------------------------------
        {
            "category": "Standard Schemes & Ports",
            "input": "Log in at https://gtbank.com/login or check local server http://127.0.0.1:8080/dashboard?user=admin&ref=1.",
            "expected": ["https://gtbank.com/login", "http://127.0.0.1:8080/dashboard?user=admin&ref=1"]
        },
        {
            "category": "Bare & Subdomain Extraction",
            "input": "Visit www.kuda.com, accessbankplc.com/help, or dev.api.portal.wema.wemabank.com/v1/test for details.",
            "expected": ["www.kuda.com", "accessbankplc.com/help", "dev.api.portal.wema.wemabank.com/v1/test"]
        },
        {
            "category": "Complex Paths, Query Params & Encoded Characters",
            "input": "Deep link: https://university.edu/~user-name/search?q=hello%20world%21&ids[]=10&ids[]=20#section-3",
            "expected": ["https://university.edu/~user-name/search?q=hello%20world%21&ids[]=10&ids[]=20#section-3"]
        },
        {
            "category": "Nested URL Parameters",
            "input": "Redirecting to https://auth.provider.com/login?continue=https://app.com/dashboard&ref=123",
            "expected": ["https://auth.provider.com/login?continue=https://app.com/dashboard&ref=123"]
        },
        {
            "category": "Punycode & IDN Domains",
            "input": "Visit international domain https://xn--e1afmkfd.xn--p1ai/test or https://münchen.de today.",
            "expected": ["https://xn--e1afmkfd.xn--p1ai/test", "https://münchen.de"]
        },

        # -------------------------------------------------------------------------
        # 2. Text Delimiters & Inline Formatting
        # -------------------------------------------------------------------------
        {
            "category": "Parentheses & Sentence Brackets",
            "input": "Please confirm your details (https://opayweb.com/verify). Nested: (https://en.wikipedia.org/wiki/Python_(programming_language)).",
            "expected": ["https://opayweb.com/verify", "https://en.wikipedia.org/wiki/Python_(programming_language)"]
        },
        {
            "category": "Markdown & HTML Enclosures",
            "input": "Click [here](https://accessbankplc.com/login) or see <a href=\"https://zenithbank.com/portal\">Link</a>.",
            "expected": ["https://accessbankplc.com/login", "https://zenithbank.com/portal"]
        },
        {
            "category": "JSON & Inline Code Delimiters",
            "input": "Config payload: {\"endpoint\": \"https://api.service.io/v2/fetch\"} |https://kuda.com/help| Website:https://firstbanknigeria.com/portal",
            "expected": ["https://api.service.io/v2/fetch", "https://kuda.com/help", "https://firstbanknigeria.com/portal"]
        },
        {
            "category": "Multiple Delimited Links",
            "input": "Links: https://kuda.com,https://opayweb.com;www.gtbank.com/login.",
            "expected": ["https://kuda.com", "https://opayweb.com", "www.gtbank.com/login"]
        },

        # -------------------------------------------------------------------------
        # 3. Security & Non-HTTP Schemes
        # -------------------------------------------------------------------------
        {
            "category": "UserInfo & Credential Obfuscation",
            "input": "Alert: http://gtbank.com@evil-domain.com/login?id=1 or ftp://user:pass@ftp.secure-host.io:21/files/",
            "expected": ["http://gtbank.com@evil-domain.com/login?id=1", "ftp://user:pass@ftp.secure-host.io:21/files/"]
        },
        {
            "category": "Executable & Data Schemes",
            "input": "Payloads: javascript:alert('xss'), data:text/html;base64,PHNjcmlwdD4..., and file:///etc/passwd",
            "expected": ["javascript:alert('xss')", "data:text/html;base64,PHNjcmlwdD4...", "file:///etc/passwd"]
        },

        # -------------------------------------------------------------------------
        # 4. False-Positive Prevention
        # -------------------------------------------------------------------------
        {
            "category": "Email Address Filtering",
            "input": "Contact support@accessbankplc.com or admin@firstbanknigeria.com for help.",
            "expected": []
        },
        {
            "category": "SSH & Git Format Filtering",
            "input": "Clone git@github.com:user/repo.git to check the code.",
            "expected": []
        },
        {
            "category": "Code Files & Plain Prose Numbers",
            "input": "Edit script.js, config.json, check version v1.2.3 or range 0.1...1.0.",
            "expected": []
        }
    ]

    print("==================================================")
    print("      ADVANCED URL EXTRACTOR TEST SUITE (31-45)   ")
    print("==================================================\n")

    passed = 0
    failed = 0

    for idx, test in enumerate(test_cases, 31):
        extracted = url_extractor_basic(test["input"])
        is_correct = extracted == test["expected"]
        
        print(f"Test {idx:02d}: [{test['category']}]")
        print(f"  Input    : \"{test['input']}\"")
        print(f"  Extracted: {extracted}")
        print(f"  Expected : {test['expected']}")
        
        if is_correct:
            print("  STATUS   : PASSED ✅\n")
            passed += 1
        else:
            print("  STATUS   : FAILED ❌\n")
            failed += 1

    print("==================================================")
    print(f"  FINAL SCORE: {passed}/{len(test_cases)} Passed")
    print("==================================================")
