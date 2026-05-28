from app.extensions import cache

class URLCache:
    @staticmethod
    def get(key):
        return cache.get(key)
    @staticmethod
    def set(key, value, timeout=300):
        cache.set(key, value, timeout=timeout)
    @staticmethod
    def delete(key):
        cache.delete(key)