import re
from urllib.parse import urlparse
from difflib import SequenceMatcher
import tldextract

COMMON_BRANDS = ['google', 'facebook', 'amazon', 'paypal', 'microsoft', 'apple', 'bankofamerica', 'chase']

class SmartDetector:
    @staticmethod
    def analyze(url):
        url = url.lower().strip()
        if not url.startswith('http'):
            url = 'http://' + url
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        extracted = tldextract.extract(url)
        
        # IP address
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            return {'is_malicious': True, 'safe': False, 'threat_category': 'malware', 'reason': 'IP address URL', 'risk_score': 95}
        # Suspicious TLDs
        suspicious_tlds = {'tk', 'ml', 'ga', 'cf', 'xyz', 'top'}
        if extracted.suffix in suspicious_tlds:
            return {'is_malicious': True, 'safe': False, 'threat_category': 'phishing', 'reason': f'Suspicious TLD .{extracted.suffix}', 'risk_score': 80}
        # @ sign
        if '@' in url:
            return {'is_malicious': True, 'safe': False, 'threat_category': 'phishing', 'reason': 'URL contains @', 'risk_score': 100}
        # Typosquatting
        if extracted.domain and extracted.suffix:
            for brand in COMMON_BRANDS:
                if extracted.domain != brand:
                    ratio = SequenceMatcher(None, extracted.domain, brand).ratio()
                    if ratio >= 0.75:
                        return {'is_malicious': True, 'safe': False, 'threat_category': 'phishing', 'reason': f'Typosquatting of {brand}', 'risk_score': 90}
        # Fake HTTPS (login over HTTP)
        if parsed.scheme == 'http' and ('login' in path or 'signin' in path):
            return {
                'is_malicious': True,
                'safe': False,
                'threat_category': 'fake_login',
                'reason': 'Login page over HTTP',
                'risk_score': 85
            }
        return {'is_malicious': False, 'safe': True, 'reason': 'No threat detected'}