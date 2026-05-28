from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phishguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------- MODELS -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True)
    category = db.Column(db.String(50))

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True)
    reason = db.Column(db.String(200))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    action = db.Column(db.String(20))
    ip = db.Column(db.String(45))
    time = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------- INITIALIZE -------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
    if Blacklist.query.count() == 0:
        for u in ['http://paypal-verify.com', 'http://appleid-verify.tk', 'http://faceb00k-login.xyz']:
            db.session.add(Blacklist(url=u, category='phishing'))
        db.session.commit()

# ------------------- HELPER FOR COMMON LAYOUT -------------------
def layout(content):
    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PhishGuard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body{{background:#0a0a0a;font-family:'Segoe UI',sans-serif;}}
    .navbar-brand{{font-weight:bold;font-size:1.5rem;}}
    .navbar-brand i{{color:#ff4444;margin-right:8px;}}
    .card{{background:#1e1e2f;border:none;border-radius:15px;box-shadow:0 6px 12px rgba(0,0,0,0.3);}}
    .card-header{{background:#2c3e50;border-radius:15px 15px 0 0 !important;font-weight:bold;}}
    .btn-danger{{background:#e74c3c;border:none;}}
    .btn-danger:hover{{background:#c0392b;transform:scale(1.02);}}
    .btn-success{{background:#2ecc71;border:none;}}
    .btn-success:hover{{background:#27ae60;transform:scale(1.02);}}
    .stat-card{{background:linear-gradient(135deg,#1e2a3a,#0f1a24);border-radius:15px;padding:1.2rem;text-align:center;}}
    .stat-value{{font-size:2.2rem;font-weight:bold;}}
    .table-dark{{background:#1a1a2e;}}
    .table-dark th{{background:#2c3e50;}}
    footer{{border-top:1px solid #2c3e50;margin-top:3rem;padding:1rem;text-align:center;color:#7f8c8d;}}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-danger">
<div class="container"><a class="navbar-brand" href="/dashboard"><i class="fas fa-shield-halt"></i> PhishGuard</a>
{ '<div><a href="/dashboard" class="btn btn-outline-light btn-sm"><i class="fas fa-tachometer-alt"></i> Dashboard</a> <a href="/blacklist" class="btn btn-outline-light btn-sm"><i class="fas fa-ban"></i> Blacklist</a> <a href="/whitelist" class="btn btn-outline-light btn-sm"><i class="fas fa-check-circle"></i> Whitelist</a> <a href="/logout" class="btn btn-light btn-sm"><i class="fas fa-sign-out-alt"></i> Logout</a></div>' if session.get('user') else '' }
</div></nav>
<div class="container mt-4">''' + content + '''</div>
<footer>&copy; 2025 PhishGuard - Real-time Phishing Protection</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body></html>'''

# ------------------- ROUTES -------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user'] = user.username
            return redirect('/dashboard')
        return layout('<div class="alert alert-danger">Invalid credentials</div><script>setTimeout(()=>location.href="/login",1500)</script>')
    return layout('''
    <div class="row justify-content-center mt-5"><div class="col-md-5">
    <div class="card border-danger"><div class="card-header bg-danger text-white text-center"><i class="fas fa-lock"></i> Admin Login</div>
    <div class="card-body"><form method="post"><div class="mb-3"><label>Username</label><input type="text" name="username" class="form-control" required></div>
    <div class="mb-4"><label>Password</label><input type="password" name="password" class="form-control" required></div>
    <button type="submit" class="btn btn-danger w-100"><i class="fas fa-sign-in-alt"></i> Login</button></form></div></div></div></div>
    ''')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    logs = Log.query.order_by(Log.time.desc()).limit(10).all()
    blocks = Log.query.filter_by(action='blocked').count()
    bl_count = Blacklist.query.count()
    wl_count = Whitelist.query.count()
    logs_html = ''
    for log in logs:
        action_html = '<span class="badge bg-danger">Blocked</span>' if log.action == 'blocked' else '<span class="badge bg-secondary">Bypassed</span>'
        logs_html += f'<tr><td style="word-break:break-all;">{log.url}</td><td>{action_html}</td><td>{log.ip}</td><td>{log.time.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>'
    content = f'''
    <h2><i class="fas fa-chart-line"></i> Security Dashboard</h2>
    <div class="row mt-3"><div class="col-md-4"><div class="stat-card"><i class="fas fa-ban fa-2x text-danger"></i><div class="stat-value">{blocks}</div><div>Total Blocks</div></div></div>
    <div class="col-md-4"><div class="stat-card"><i class="fas fa-link fa-2x text-info"></i><div class="stat-value">{bl_count}</div><div>Blacklisted URLs</div></div></div>
    <div class="col-md-4"><div class="stat-card"><i class="fas fa-check-circle fa-2x text-success"></i><div class="stat-value">{wl_count}</div><div>Whitelisted URLs</div></div></div></div>
    <div class="card mt-4"><div class="card-header"><i class="fas fa-check-circle"></i> URL Checker</div><div class="card-body">
    <form method="post" action="/check"><div class="input-group"><input type="url" name="url" class="form-control" placeholder="Enter URL to check (e.g., http://example.com)" required><button class="btn btn-danger" type="submit"><i class="fas fa-search"></i> Check Now</button></div></form>
    <small class="text-muted">Enter any URL – if blacklisted, you'll see a warning page.</small></div></div>
    <div class="card mt-4"><div class="card-header"><i class="fas fa-history"></i> Recent Blocked Attempts</div><div class="card-body"><div class="table-responsive"><table class="table table-dark table-hover"><thead><tr><th>URL</th><th>Action</th><th>IP</th><th>Time</th></tr></thead><tbody>{logs_html}</tbody></table></div></div></div>
    '''
    return layout(content)

@app.route('/blacklist')
def blacklist():
    if 'user' not in session:
        return redirect('/login')
    urls = Blacklist.query.all()
    rows = ''
    for u in urls:
        rows += f'<tr><td style="word-break:break-all;">{u.url}</td><td><span class="badge bg-danger">{u.category}</span></td><td><a href="/delete_blacklist/{u.id}" class="btn btn-sm btn-warning" onclick="return confirm(\'Delete?\')"><i class="fas fa-trash"></i> Delete</a></td></tr>'
    content = f'''
    <h2><i class="fas fa-ban"></i> Blacklist Manager</h2>
    <div class="card mb-4"><div class="card-header bg-danger text-white"><i class="fas fa-plus-circle"></i> Add Malicious URL</div><div class="card-body">
    <form method="post" action="/add_blacklist" class="row g-2"><div class="col-md-6"><input type="url" name="url" class="form-control" placeholder="https://evil.com" required></div>
    <div class="col-md-3"><select name="cat" class="form-select"><option>phishing</option><option>malware</option><option>scam</option><option>fake_banking</option><option>fake_login</option></select></div>
    <div class="col-md-3"><button class="btn btn-danger w-100"><i class="fas fa-plus"></i> Add to Blacklist</button></div></form></div></div>
    <div class="card"><div class="card-header"><i class="fas fa-list"></i> Current Blacklist ({len(urls)} entries)</div><div class="card-body"><div class="table-responsive"><table class="table table-dark table-striped"><thead><tr><th>URL</th><th>Category</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
    '''
    return layout(content)

@app.route('/add_blacklist', methods=['POST'])
def add_blacklist():
    if 'user' not in session:
        return redirect('/login')
    url = request.form['url'].strip()
    cat = request.form['cat']
    if url and not Blacklist.query.filter_by(url=url).first():
        db.session.add(Blacklist(url=url, category=cat))
        db.session.commit()
    return redirect('/blacklist')

@app.route('/delete_blacklist/<int:id>')
def delete_blacklist(id):
    if 'user' not in session:
        return redirect('/login')
    item = Blacklist.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect('/blacklist')

# ------------------- WHITELIST ROUTES -------------------
@app.route('/whitelist')
def whitelist():
    if 'user' not in session:
        return redirect('/login')
    urls = Whitelist.query.all()
    rows = ''
    for u in urls:
        rows += f'<td><td style="word-break:break-all;">{u.url}</td><td>{u.reason or "-"}</td><td>{u.added_at.strftime("%Y-%m-%d")}</td><td><a href="/delete_whitelist/{u.id}" class="btn btn-sm btn-danger" onclick="return confirm(\'Remove from whitelist?\')"><i class="fas fa-trash"></i> Remove</a></td></tr>'
    content = f'''
    <h2><i class="fas fa-check-circle"></i> Whitelist Manager</h2>
    <div class="card mb-4"><div class="card-header bg-success text-white"><i class="fas fa-plus-circle"></i> Add Trusted URL</div><div class="card-body">
    <form method="post" action="/add_whitelist" class="row g-2"><div class="col-md-6"><input type="url" name="url" class="form-control" placeholder="https://trusted.com" required></div>
    <div class="col-md-4"><input type="text" name="reason" class="form-control" placeholder="Reason (e.g., Internal tool)"></div>
    <div class="col-md-2"><button class="btn btn-success w-100"><i class="fas fa-plus"></i> Add to Whitelist</button></div></form></div></div>
    <div class="card"><div class="card-header"><i class="fas fa-list"></i> Current Whitelist ({len(urls)} entries)</div><div class="card-body"><div class="table-responsive"><table class="table table-dark table-striped"><thead><tr><th>URL</th><th>Reason</th><th>Added</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
    '''
    return layout(content)

@app.route('/add_whitelist', methods=['POST'])
def add_whitelist():
    if 'user' not in session:
        return redirect('/login')
    url = request.form['url'].strip()
    reason = request.form.get('reason', '')
    if url and not Whitelist.query.filter_by(url=url).first():
        db.session.add(Whitelist(url=url, reason=reason))
        db.session.commit()
    return redirect('/whitelist')

@app.route('/delete_whitelist/<int:id>')
def delete_whitelist(id):
    if 'user' not in session:
        return redirect('/login')
    item = Whitelist.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect('/whitelist')

@app.route('/check', methods=['POST'])
def check():
    if 'user' not in session:
        return redirect('/login')
    target = request.form.get('url')
    if not target:
        return redirect('/dashboard')
    if not target.startswith('http'):
        target = 'http://' + target
    
    # Check whitelist first
    if Whitelist.query.filter_by(url=target).first():
        db.session.add(Log(url=target, action='whitelisted', ip=request.remote_addr))
        db.session.commit()
        return redirect(target)
    
    # Check blacklist
    blocked = Blacklist.query.filter_by(url=target).first()
    if blocked:
        db.session.add(Log(url=target, action='blocked', ip=request.remote_addr))
        db.session.commit()
        return f'''<!DOCTYPE html><html><head><title>Warning</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/css/bootstrap.min.css" rel="stylesheet"><style>body{{background:#1a0000;text-align:center;padding:50px;}}.box{{background:#2a0000;border:3px solid red;border-radius:20px;padding:40px;max-width:600px;margin:auto;color:white;box-shadow:0 0 30px rgba(255,0,0,0.5);}}h1{{color:red;font-size:48px;}}.url{{background:black;padding:10px;border-radius:10px;word-break:break-all;}}</style></head><body><div class="box"><i class="fas fa-skull-crossbow" style="font-size:80px;color:red"></i><h1>⚠️ DANGER ⚠️</h1><p><strong>Reason:</strong> Blacklisted as {blocked.category}</p><div class="url">{target}</div><form method="post" action="/proceed"><input type="hidden" name="url" value="{target}"><button type="button" class="btn btn-secondary" onclick="history.back()">Go Back</button><button type="submit" class="btn btn-danger" onclick="return confirm('Proceed anyway?')">Proceed Anyway</button></form></div><script src="https://kit.fontawesome.com/a076d05399.js"></script></body></html>'''
    else:
        db.session.add(Log(url=target, action='bypassed', ip=request.remote_addr))
        db.session.commit()
        return redirect(target)

@app.route('/proceed', methods=['POST'])
def proceed():
    if 'user' not in session:
        return redirect('/login')
    target = request.form.get('url')
    if target:
        db.session.add(Log(url=target, action='bypassed', ip=request.remote_addr))
        db.session.commit()
        return redirect(target)
    return redirect('/dashboard')

@app.route('/')
def home():
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)