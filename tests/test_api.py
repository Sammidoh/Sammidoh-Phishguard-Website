import unittest
import json
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.blacklist import BlacklistedURL
from app.models.threat_category import ThreatCategory

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Create admin user
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            # Add a threat category
            cat = ThreatCategory(name='phishing')
            db.session.add(cat)
            db.session.commit()
            # Add a blacklisted URL
            bl = BlacklistedURL(url='http://evil.com', category_id=cat.id)
            db.session.add(bl)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_check_url_safe(self):
        response = self.client.post('/api/v1/check',
                                    data=json.dumps({'url': 'https://google.com'}),
                                    content_type='application/json')
        data = response.get_json()
        self.assertTrue(data['safe'])

    def test_check_url_blacklisted(self):
        response = self.client.post('/api/v1/check',
                                    data=json.dumps({'url': 'http://evil.com'}),
                                    content_type='application/json')
        data = response.get_json()
        self.assertFalse(data['safe'])
        self.assertEqual(data['threat_category'], 'phishing')

    def test_logs_endpoint(self):
        response = self.client.get('/logs/data')
        self.assertEqual(response.status_code, 302)  # Redirects to login
        # Simulate login
        with self.client:
            self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
            response = self.client.get('/logs/data')
            self.assertEqual(response.status_code, 200)

    def test_stats_endpoint(self):
        with self.client:
            self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
            response = self.client.get('/logs/stats')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('total_blocks', data)

if __name__ == '__main__':
    unittest.main()