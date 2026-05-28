from app.models.blacklist import BlacklistedURL
from app.models.whitelist import WhitelistedURL
from app.services.smart_detector import SmartDetector
from app.extensions import cache

class URLChecker:
    @staticmethod
    @cache.memoize(timeout=300)
    def check(url, user_settings=None):
        if user_settings and not user_settings.protection_enabled:
            return {'safe': True, 'reason': 'Protection disabled'}
        # 1. Whitelist
        if WhitelistedURL.query.filter_by(url=url).first():
            return {'safe': True, 'reason': 'Whitelisted'}
        # 2. Blacklist
        bl = BlacklistedURL.query.filter_by(url=url).first()
        if bl:
            return {
                'safe': False,
                'threat_category': bl.category.name if bl.category else 'unknown',
                'reason': f'Exact blacklist match',
                'risk_score': bl.risk_score
            }
        # 3. Heuristics
        heuristic_result = SmartDetector.analyze(url)
        if heuristic_result['is_malicious']:
            return heuristic_result
        return {'safe': True, 'reason': 'No threat detected'}