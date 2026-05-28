from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app.models.setting import UserSettings
from app.extensions import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            # Ensure user settings exist
            if not UserSettings.query.filter_by(user_id=user.id).first():
                db.session.add(UserSettings(user_id=user.id))
                db.session.commit()
            return redirect(url_for('dashboard.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))