import os
import json
import re
from datetime import datetime
from functools import wraps
from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phishguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------- MODELS -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    category = db.Column(db.String(50))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    reason = db.Column(db.String(200))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class AILog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    ai_score = db.Column(db.Integer)
    ai_reason = db.Column(db.String(500))
    user_action = db.Column(db.String(20))
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BlockedLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    threat_category = db.Column(db.String(50))
    user_action = db.Column(db.String(20))
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------- INIT -------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created: admin / admin123")
    if Blacklist.query.count() == 0:
        for url, cat in [('http://paypal-verify.com', 'phishing'), ('http://appleid-verify.tk', 'phishing')]:
            db.session.add(Blacklist(url=url, category=cat))
        db.session.commit()

# ------------------- AI HELPER (Groq) -------------------
if GROQ_AVAILABLE:
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    def ai_analyze(url):
        try:
            prompt = f"""Analyze this URL: {url}
Return ONLY a valid JSON object with two fields:
- "score": integer from 0 to 100 (0 = safe, 100 = extremely dangerous phishing/malware)
- "reason": short one-sentence explanation (max 20 words)

Example: {{"score": 95, "reason": "Typosquatting of PayPal"}}
Do not include any other text, only the JSON."""
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a security classifier. Output ONLY a JSON object. No other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=100
            )
            content = response.choices[0].message.content.strip()
            # Extract JSON (in case model adds backticks or extra text)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            result = json.loads(content)
            score = int(result.get('score', 0))
            reason = result.get('reason', 'No reason given')
            # Clamp to 0-100
            score = max(0, min(100, score))
            return score, reason
        except Exception as e:
            app.logger.error(f"Groq AI error: {e}")
            return None, None
else:
    def ai_analyze(url):
        return None, None

# ------------------- AUTH DECORATOR -------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ------------------- ROUTES -------------------
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/dashboard')
        return '<div class="alert alert-danger">Invalid credentials</div><script>setTimeout(()=>location.href="/login",1500)</script>'
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
@login_required
def dashboard():
    total_blocks = BlockedLog.query.count()
    blacklist_count = Blacklist.query.count()
    whitelist_count = Whitelist.query.count()
    recent = BlockedLog.query.order_by(BlockedLog.timestamp.desc()).limit(10).all()
    logs_html = ''.join(f'<tr><td style="word-break:break-all;">{l.url}</td><td>{l.threat_category or "-"}</td><td>{l.user_action}</td><td>{l.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>' for l in recent)
    content = DASHBOARD_HTML.format(total_blocks=total_blocks, blacklist_count=blacklist_count, whitelist_count=whitelist_count, logs_html=logs_html)
    return render_template_string(content)

@app.route('/blacklist', methods=['GET', 'POST'])
@login_required
def blacklist():
    if request.method == 'POST':
        url = request.form.get('url')
        cat = request.form.get('category', 'phishing')
        if url and not Blacklist.query.filter_by(url=url).first():
            db.session.add(Blacklist(url=url, category=cat))
            db.session.commit()
        return redirect('/blacklist')
    items = Blacklist.query.all()
    rows = ''.join(f'<tr><td style="word-break:break-all;">{i.url}</td><td>{i.category}</td><td>{i.added_at.strftime("%Y-%m-%d")}</td><td><a href="/delete_blacklist/{i.id}" class="btn btn-sm btn-danger" onclick="return confirm(\'Delete?\')">Delete</a></td></tr>' for i in items)
    return render_template_string(BLACKLIST_HTML.format(rows=rows, count=len(items)))

@app.route('/delete_blacklist/<int:id>')
@login_required
def delete_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/blacklist')

@app.route('/whitelist', methods=['GET', 'POST'])
@login_required
def whitelist():
    if request.method == 'POST':
        url = request.form.get('url')
        reason = request.form.get('reason', '')
        if url and not Whitelist.query.filter_by(url=url).first():
            db.session.add(Whitelist(url=url, reason=reason))
            db.session.commit()
        return redirect('/whitelist')
    items = Whitelist.query.all()
    rows = ''.join(f'<tr><td style="word-break:break-all;">{i.url}</td><td>{i.reason}</td><td>{i.added_at.strftime("%Y-%m-%d")}</td><td><a href="/delete_whitelist/{i.id}" class="btn btn-sm btn-warning" onclick="return confirm(\'Remove?\')">Remove</a></td></tr>' for i in items)
    return render_template_string(WHITELIST_HTML.format(rows=rows, count=len(items)))

@app.route('/delete_whitelist/<int:id>')
@login_required
def delete_whitelist(id):
    item = Whitelist.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/whitelist')

@app.route('/logs')
@login_required
def logs():
    items = BlockedLog.query.order_by(BlockedLog.timestamp.desc()).all()
    rows = ''.join(f'<tr><td style="word-break:break-all;">{l.url}</td><td>{l.threat_category or "-"}</td><td>{l.user_action}</td><td>{l.ip_address}</td><td>{l.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>' for l in items)
    return render_template_string(LOGS_HTML.format(rows=rows, count=len(items)))

@app.route('/check', methods=['POST'])
@login_required
def check():
    target = request.form.get('url')
    if not target:
        return redirect('/dashboard')
    if not target.startswith('http'):
        target = 'http://' + target

    # 1. Whitelist
    if Whitelist.query.filter_by(url=target).first():
        db.session.add(BlockedLog(url=target, user_action='whitelisted', ip_address=request.remote_addr))
        db.session.commit()
        return redirect(target)

    # 2. Local blacklist
    bl = Blacklist.query.filter_by(url=target).first()
    if bl:
        db.session.add(BlockedLog(url=target, threat_category=bl.category, user_action='blocked_by_blacklist', ip_address=request.remote_addr))
        db.session.commit()
        return render_template_string(DENIED_HTML, url=target, reason=f"Blacklisted as {bl.category}", score='N/A')

    # 3. Groq AI analysis
    if GROQ_AVAILABLE:
        score, reason = ai_analyze(target)
        if score is not None:
            db.session.add(AILog(url=target, ai_score=score, ai_reason=reason, user_action='blocked_by_ai' if score >= 75 else 'allowed', ip_address=request.remote_addr))
            db.session.commit()
            if score >= 75:
                db.session.add(BlockedLog(url=target, threat_category=f"AI: {reason[:50]}", user_action='blocked_by_ai', ip_address=request.remote_addr))
                db.session.commit()
                return render_template_string(DENIED_HTML, url=target, reason=reason, score=score)
    # 4. Allow
    db.session.add(BlockedLog(url=target, user_action='allowed', ip_address=request.remote_addr))
    db.session.commit()
    return redirect(target)

# ------------------- HTML TEMPLATES (embedded) -------------------
BASE_HEAD = '''<!DOCTYPE html>
<html><head><title>PhishGuard</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-dark"><nav class="navbar navbar-dark bg-danger"><div class="container"><a class="navbar-brand" href="/dashboard">🛡️ PhishGuard</a>
<div><a href="/dashboard" class="btn btn-outline-light btn-sm">Dashboard</a>
<a href="/blacklist" class="btn btn-outline-light btn-sm">Blacklist</a>
<a href="/whitelist" class="btn btn-outline-light btn-sm">Whitelist</a>
<a href="/logs" class="btn btn-outline-light btn-sm">Logs</a>
<a href="/logout" class="btn btn-light btn-sm">Logout</a></div></div></nav>
<div class="container mt-4">'''
BASE_FOOT = '''</div><footer class="text-center text-muted mt-5">PhishGuard - AI powered by Groq</footer></body></html>'''

LOGIN_HTML = '''<!DOCTYPE html><html><head><title>Login</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-dark"><div class="container mt-5"><div class="row justify-content-center"><div class="col-md-4"><div class="card"><div class="card-header bg-danger text-white">Login</div>
<div class="card-body"><form method="post"><div class="mb-3"><input type="text" name="username" class="form-control" placeholder="Username" required></div>
<div class="mb-3"><input type="password" name="password" class="form-control" placeholder="Password" required></div>
<button type="submit" class="btn btn-danger w-100">Login</button></form></div></div></div></div></div></body></html>'''

DASHBOARD_HTML = BASE_HEAD + '''
<h2>Dashboard</h2><div class="row"><div class="col-md-4"><div class="card bg-danger text-white"><div class="card-body"><h5>Total Blocks</h5><h1>{total_blocks}</h1></div></div></div>
<div class="col-md-4"><div class="card bg-info text-white"><div class="card-body"><h5>Blacklisted URLs</h5><h1>{blacklist_count}</h1></div></div></div>
<div class="col-md-4"><div class="card bg-success text-white"><div class="card-body"><h5>Whitelisted URLs</h5><h1>{whitelist_count}</h1></div></div></div></div>
<div class="card mt-4"><div class="card-header">URL Checker</div><div class="card-body"><form method="post" action="/check"><div class="input-group"><input type="url" name="url" class="form-control" required><button class="btn btn-danger">Analyze</button></div></form></div></div>
<div class="card mt-4"><div class="card-header">Recent Blocks</div><div class="card-body"><div class="table-responsive"><table class="table table-dark"><thead><tr><th>URL</th><th>Threat</th><th>Action</th><th>Time</th></tr></thead><tbody>{logs_html}</tbody></table></div></div></div>
''' + BASE_FOOT

BLACKLIST_HTML = BASE_HEAD + '''
<h2>Blacklist Manager</h2><div class="card mb-3"><div class="card-header">Add URL</div><div class="card-body"><form method="post" class="row"><div class="col-md-6"><input name="url" class="form-control" placeholder="https://evil.com" required></div>
<div class="col-md-3"><select name="category" class="form-select"><option>phishing</option><option>malware</option><option>scam</option></select></div><div class="col-md-3"><button class="btn btn-danger">Add</button></div></form></div></div>
<div class="card"><div class="card-header">Current Blacklist ({count})</div><div class="card-body"><div class="table-responsive"><table class="table table-dark">{rows}</td></div></div></div>
''' + BASE_FOOT

WHITELIST_HTML = BASE_HEAD + '''
<h2>Whitelist Manager</h2><div class="card mb-3"><div class="card-header">Add Trusted URL</div><div class="card-body"><form method="post" class="row"><div class="col-md-6"><input name="url" class="form-control" placeholder="https://trusted.com" required></div>
<div class="col-md-4"><input name="reason" class="form-control" placeholder="Reason"></div><div class="col-md-2"><button class="btn btn-success">Add</button></div></form></div></div>
<div class="card"><div class="card-header">Whitelisted URLs ({count})</div><div class="card-body"><div class="table-responsive"><table class="table table-dark">{rows}</table></div></div></div>
''' + BASE_FOOT

LOGS_HTML = BASE_HEAD + '''
<h2>All Logs</h2><div class="card"><div class="card-header">Blocked Attempts ({count})</div><div class="card-body"><div class="table-responsive"><table class="table table-dark"><thead><tr><th>URL</th><th>Threat</th><th>Action</th><th>IP</th><th>Time</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
''' + BASE_FOOT

DENIED_HTML = '''<!DOCTYPE html><html><head><title>Blocked</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-dark"><div class="container mt-5"><div class="alert alert-danger text-center"><h1>⛔ Access Denied</h1><p>URL: <strong>{url}</strong></p><p>Reason: {reason}</p><p>AI Score: {score}</p><a href="/dashboard" class="btn btn-primary">Back to Dashboard</a></div></div></body></html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)