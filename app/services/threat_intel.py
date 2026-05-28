import csv
from app.extensions import db
from app.models.blacklist import BlacklistedURL
from app.models.threat_category import ThreatCategory

class ThreatIntel:
    @staticmethod
    def import_csv(file_path, category_name='phishing'):
        cat = ThreatCategory.query.filter_by(name=category_name).first()
        if not cat:
            cat = ThreatCategory(name=category_name)
            db.session.add(cat)
            db.session.commit()
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                url = row[0].strip()
                if url and not BlacklistedURL.query.filter_by(url=url).first():
                    db.session.add(BlacklistedURL(url=url, category_id=cat.id, risk_score=90))
        db.session.commit()