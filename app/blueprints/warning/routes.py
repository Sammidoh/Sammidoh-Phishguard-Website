from flask import Blueprint, render_template, request, redirect, make_response
from app.models.log import BlockedLog
from app.extensions import db

bp = Blueprint('warning', __name__)

@bp.route('/show')
def show():
    url = request.args.get('url', '#')
    reason = request.args.get('reason', 'This site is dangerous')
    category = request.args.get('category', 'phishing')
    return render_template('warning/warning.html', url=url, reason=reason, category=category)

@bp.route('/proceed', methods=['POST'])
def proceed():
    target = request.form.get('url')
    category = request.form.get('category', 'unknown')
    if not target:
        return redirect('/')
    log = BlockedLog(
        url=target,
        threat_category=category,
        user_action='bypass',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log)
    db.session.commit()
    resp = make_response(redirect(target))
    resp.set_cookie('bypass_token', 'allowed', max_age=300, httponly=True)
    return resp