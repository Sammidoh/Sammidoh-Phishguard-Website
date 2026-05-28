from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.whitelist import WhitelistedURL

bp = Blueprint('whitelist', __name__)

@bp.route('/')
@login_required
def list_whitelist():
    urls = WhitelistedURL.query.all()
    return render_template('whitelist/list.html', urls=urls)

@bp.route('/data')
@login_required
def data():
    urls = WhitelistedURL.query.all()
    return jsonify([{'id': u.id, 'url': u.url, 'reason': u.reason, 'added_at': u.added_at.isoformat()} for u in urls])

@bp.route('/add', methods=['GET'])
@login_required
def add_form():
    return render_template('whitelist/add.html')

@bp.route('/add', methods=['POST'])
@login_required
def add():
    url = request.form.get('url')
    reason = request.form.get('reason', '')
    if url and not WhitelistedURL.query.filter_by(url=url).first():
        db.session.add(WhitelistedURL(url=url, reason=reason))
        db.session.commit()
    return redirect(url_for('whitelist.list_whitelist'))

@bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_form(id):
    entry = WhitelistedURL.query.get_or_404(id)
    return render_template('whitelist/edit.html', entry=entry)

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    entry = WhitelistedURL.query.get_or_404(id)
    entry.url = request.form['url']
    entry.reason = request.form.get('reason', '')
    db.session.commit()
    return redirect(url_for('whitelist.list_whitelist'))

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    entry = WhitelistedURL.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('whitelist.list_whitelist'))