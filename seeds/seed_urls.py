# seeds/seed_urls.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from app.extensions import db
from app.models.threat_category import ThreatCategory
from app.models.blacklist import BlacklistedURL
from app.models.user import User
import csv

def seed():
    app = create_app()
    with app.app_context():
        # Ensure categories exist
        categories = ['phishing', 'malware', 'scam', 'fake_banking', 'fake_login']
        for cat_name in categories:
            if not ThreatCategory.query.filter_by(name=cat_name).first():
                db.session.add(ThreatCategory(name=cat_name))
        db.session.commit()

        # Import URLs from CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'phishing_urls.csv')
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} not found")
            return
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                url = row['url'].strip()
                cat_name = row['category'].strip()
                cat = ThreatCategory.query.filter_by(name=cat_name).first()
                if cat and not BlacklistedURL.query.filter_by(url=url).first():
                    db.session.add(BlacklistedURL(url=url, category_id=cat.id, risk_score=90))
                    count += 1
        db.session.commit()
        print(f"Imported {count} blacklisted URLs")

        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    seed()