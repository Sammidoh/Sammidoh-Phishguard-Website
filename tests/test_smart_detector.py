import unittest
from app.services.smart_detector import SmartDetector

class TestSmartDetector(unittest.TestCase):
    def test_ip_detection(self):
        result = SmartDetector.analyze('http://10.0.0.1')
        self.assertFalse(result['safe'])
        self.assertEqual(result['threat_category'], 'malware')
        self.assertIn('IP address', result['reason'])

    def test_suspicious_tld(self):
        result = SmartDetector.analyze('http://evil.xyz')
        self.assertFalse(result['safe'])
        self.assertIn('Suspicious TLD', result['reason'])

    def test_at_sign(self):
        result = SmartDetector.analyze('http://secure@paypal.com')
        self.assertFalse(result['safe'])
        self.assertIn('@', result['reason'])

    def test_typosquatting(self):
        result = SmartDetector.analyze('http://paypa1.com')
        # Should detect typosquatting of 'paypal'
        self.assertFalse(result['safe'])
        self.assertEqual(result['threat_category'], 'phishing')
        self.assertIn('Typosquatting', result['reason'])

    def test_safe_url(self):
        result = SmartDetector.analyze('https://github.com')
        # Should be safe
        self.assertTrue(result['is_malicious'] is False or result.get('safe', True))

if __name__ == '__main__':
    unittest.main()