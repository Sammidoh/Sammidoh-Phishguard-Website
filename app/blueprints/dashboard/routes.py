from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html')

@bp.route('/analytics')
@login_required
def analytics():
    return render_template('dashboard/analytics.html')

@bp.route('/settings')
@login_required
def settings():
    return render_template('dashboard/settings.html')