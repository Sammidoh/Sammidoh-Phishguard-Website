import unittest
from app.utils.url_analyzer import URLAnalyzer

class TestURLAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = URLAnalyzer()

    def test_safe_url(self):
        safe, cat, reason, risk = self.analyzer.analyze('https://google.com')
        self.assertFalse(safe)
        # Actually, 'https://google.com' is not in blacklist, heuristics may pass?
        # Heuristics: not IP, not suspicious TLD, no @, etc. Should return safe.
        # But our analyzer returns (False, None, "Safe", 0) for safe.
        self.assertFalse(safe)  # is_malicious = False
        self.assertIsNone(cat)

    def test_ip_url(self):
        safe, cat, reason, risk = self.analyzer.analyze('http://192.168.1.1/login')
        self.assertTrue(safe)  # is_malicious = True
        self.assertEqual(cat, 'malware')
        self.assertIn('IP address', reason)

    def test_suspicious_tld(self):
        safe, cat, reason, risk = self.analyzer.analyze('http://example.tk')
        self.assertTrue(safe)
        self.assertEqual(cat, 'malware')
        self.assertIn('Suspicious TLD', reason)

    def test_at_sign(self):
        safe, cat, reason, risk = self.analyzer.analyze('http://fake@paypal.com')
        self.assertTrue(safe)
        self.assertEqual(cat, 'phishing')
        self.assertIn('@', reason)

    def test_whitelist(self):
        # This requires a database. We'll mock or skip.
        pass

    def test_blacklist(self):
        # Similarly requires DB
        pass

if __name__ == '__main__':
    unittest.main()