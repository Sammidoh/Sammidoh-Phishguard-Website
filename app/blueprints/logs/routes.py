from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.log import BlockedLog
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('logs', __name__)

@bp.route('/')
@login_required
def list_logs():
    return render_template('logs/list.html')

@bp.route('/data')
@login_required
def data():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    category = request.args.get('category')
    query = BlockedLog.query
    if category:
        query = query.filter_by(threat_category=category)
    paginated = query.order_by(desc(BlockedLog.timestamp)).paginate(page=page, per_page=per_page, error_out=False)
    logs = [{
        'id': l.id,
        'url': l.url,
        'threat_category': l.threat_category,
        'user_action': l.user_action,
        'ip_address': l.ip_address,
        'timestamp': l.timestamp.isoformat(),
        'risk_score': l.risk_score
    } for l in paginated.items]
    return jsonify({'logs': logs, 'total': paginated.total, 'page': page, 'pages': paginated.pages})

@bp.route('/stats')
@login_required
def stats():
    total_blocks = BlockedLog.query.filter_by(user_action='blocked').count()
    total_bypass = BlockedLog.query.filter_by(user_action='bypass').count()
    last_7_days = []
    for i in range(7):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = BlockedLog.query.filter(func.date(BlockedLog.timestamp) == day).count()
        last_7_days.append({'date': day.isoformat(), 'count': count})
    return jsonify({'total_blocks': total_blocks, 'total_bypass': total_bypass, 'daily': last_7_days})