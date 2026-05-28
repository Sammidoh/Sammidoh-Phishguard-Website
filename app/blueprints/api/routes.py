from flask import Blueprint, request, jsonify, current_app
from app.services.url_checker import URLChecker
from app.models.api_key import APIKey
from app.models.log import BlockedLog
from app.extensions import db, limiter as limiter_ext
from datetime import datetime
import secrets

bp = Blueprint('api', __name__)

def verify_api_key():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return None
    key = auth.split(' ')[1]
    api_key = APIKey.query.filter_by(key=key, is_active=True).first()
    if api_key:
        api_key.last_used = datetime.utcnow()
        db.session.commit()
        return api_key
    return None

@bp.route('/check', methods=['POST'])
@limiter_ext.limit('100 per minute')
def check_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing url'}), 400
    url = data['url']
    api_key = verify_api_key()
    user_settings = None
    if api_key:
        from app.models.setting import UserSettings
        user_settings = UserSettings.query.filter_by(user_id=api_key.user_id).first()
    result = URLChecker.check(url, user_settings)
    if not result['safe']:
        log = BlockedLog(
            url=url,
            threat_category=result['threat_category'],
            user_action='blocked',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            risk_score=result['risk_score']
        )
        db.session.add(log)
        db.session.commit()
    return jsonify(result)

@bp.route('/scan', methods=['POST'])
def scan_bulk():
    # For future bulk scanning
    return jsonify({'message': 'Bulk scan endpoint (to be implemented)'})