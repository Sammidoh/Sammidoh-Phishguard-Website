from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, csrf, cache, limiter
import os

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Import and register blueprints
    from app.blueprints.auth.routes import bp as auth_bp
    from app.blueprints.dashboard.routes import bp as dashboard_bp
    from app.blueprints.blacklist.routes import bp as blacklist_bp
    from app.blueprints.whitelist.routes import bp as whitelist_bp
    from app.blueprints.api.routes import bp as api_bp
    from app.blueprints.logs.routes import bp as logs_bp
    from app.blueprints.warning.routes import bp as warning_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(blacklist_bp, url_prefix='/blacklist')
    app.register_blueprint(whitelist_bp, url_prefix='/whitelist')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(logs_bp, url_prefix='/logs')
    app.register_blueprint(warning_bp, url_prefix='/warning')

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app