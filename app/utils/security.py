import secrets
from werkzeug.security import generate_password_hash, check_password_hash

def generate_token(length=32):
    return secrets.token_urlsafe(length)

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed, plain):
    return check_password_hash(hashed, plain)