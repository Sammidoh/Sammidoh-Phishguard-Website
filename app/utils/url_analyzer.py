from urllib.parse import urlparse
import re
import tldextract

class URLAnalyzer:
    def analyze(self, url):
        url = url.strip()
        if not url:
            return False, None, 'Invalid URL', 0

        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        parsed = urlparse(url)
        extracted = tldextract.extract(url)
        netloc = parsed.netloc.lower()

        # IP address detection
        if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', netloc):
            return True, 'malware', 'IP address URL', 95

        # Suspicious TLDs
        suspicious_tlds = {'tk', 'ml', 'ga', 'cf', 'xyz', 'top'}
        if extracted.suffix in suspicious_tlds:
            return True, 'malware', f'Suspicious TLD .{extracted.suffix}', 80

        # @ sign in URL
        if '@' in url:
            return True, 'phishing', 'URL contains @', 100

        # Fake login pages over HTTP
        if parsed.scheme == 'http' and any(keyword in parsed.path for keyword in ('login', 'signin', 'verify')):
            return True, 'phishing', 'Login page over HTTP', 85

        return False, None, 'Safe', 0
