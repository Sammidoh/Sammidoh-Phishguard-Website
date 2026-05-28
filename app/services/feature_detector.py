import re
from urllib.parse import urlparse
import math

class FeatureExtractor:
    @staticmethod
    def extract(url):
        features = {}
        features['length'] = len(url)
        features['dot_count'] = url.count('.')
        features['hyphen_count'] = url.count('-')
        features['digit_count'] = sum(c.isdigit() for c in url)
        features['special_chars'] = len(re.findall(r'[^a-zA-Z0-9\.\-_:/\?=&#]', url))
        features['has_https'] = 1 if url.startswith('https') else 0
        features['has_at'] = 1 if '@' in url else 0
        features['subdomain_depth'] = url.count('.')
        return features