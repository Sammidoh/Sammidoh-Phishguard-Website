from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.blacklist import BlacklistedURL
from app.models.threat_category import ThreatCategory

bp = Blueprint('blacklist', __name__)

@bp.route('/')
@login_required
def list_blacklist():
    urls = BlacklistedURL.query.all()
    return render_template('blacklist/list.html', urls=urls)

@bp.route('/data')
@login_required
def data():
    urls = BlacklistedURL.query.all()
    return jsonify([{
        'id': u.id,
        'url': u.url,
        'category': u.category.name if u.category else 'unknown',
        'risk_score': u.risk_score,
        'added_at': u.added_at.isoformat()
    } for u in urls])

@bp.route('/add', methods=['GET'])
@login_required
def add_form():
    return render_template('blacklist/add.html')

@bp.route('/add', methods=['POST'])
@login_required
def add():
    url = request.form.get('url')
    category_name = request.form.get('category', 'phishing')
    risk = int(request.form.get('risk_score', 100))
    
    cat = ThreatCategory.query.filter_by(name=category_name).first()
    if not cat:
        cat = ThreatCategory(name=category_name)
        db.session.add(cat)
        db.session.commit()
    
    if not BlacklistedURL.query.filter_by(url=url).first():
        new_url = BlacklistedURL(
            url=url,
            category_id=cat.id,
            risk_score=risk,
            added_by=current_user.username
        )
        db.session.add(new_url)
        db.session.commit()
    return redirect(url_for('blacklist.list_blacklist'))

@bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_form(id):
    url = BlacklistedURL.query.get_or_404(id)
    return render_template('blacklist/edit.html', url=url)

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    entry = BlacklistedURL.query.get_or_404(id)
    entry.url = request.form['url']
    category_name = request.form['category']
    cat = ThreatCategory.query.filter_by(name=category_name).first()
    if cat:
        entry.category_id = cat.id
    entry.risk_score = int(request.form.get('risk_score', 100))
    db.session.commit()
    return redirect(url_for('blacklist.list_blacklist'))

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    entry = BlacklistedURL.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('blacklist.list_blacklist'))