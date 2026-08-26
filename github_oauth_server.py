#!/usr/bin/env python3
import os, json, subprocess, tempfile
from flask import Flask, request, jsonify, session, redirect
from flask_talisman import Talisman
from flask_session import Session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ---- Encryption using openssl (optional) ----
def openssl_encrypt(data):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(data)
        f.flush()
        key = os.getenv('ENCRYPTION_KEY') or open('.encryption_key').read().strip()
        cmd = f"openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:{key} -in {f.name} -base64"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        os.unlink(f.name)
        if result.returncode != 0:
            raise Exception("Encryption failed")
        return result.stdout.strip()

def openssl_decrypt(encrypted_data):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(encrypted_data)
        f.flush()
        key = os.getenv('ENCRYPTION_KEY') or open('.encryption_key').read().strip()
        cmd = f"openssl enc -d -aes-256-cbc -salt -pbkdf2 -pass pass:{key} -in {f.name} -base64"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        os.unlink(f.name)
        if result.returncode != 0:
            raise Exception("Decryption failed")
        return result.stdout

# ---- Secure session ----
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
Session(app)

# ---- Talisman ----
Talisman(app,
         force_https=True,
         content_security_policy={
             'default-src': "'self'",
             'script-src': ["'self'", "https://cdn.jsdelivr.net"],
             'style-src': ["'self'", "'unsafe-inline'"],
             'img-src': ["'self'", "data:"],
         })

# ---- Admin wallet ----
ADMIN_WALLET = os.getenv("ADMIN_WALLET")
if not ADMIN_WALLET:
    raise Exception("ADMIN_WALLET not set in .env")

# ---- Middleware: decrypt incoming JSON (optional) ----
@app.before_request
def decrypt_payload():
    if request.is_json and request.method in ['POST', 'PUT', 'PATCH']:
        try:
            data = request.get_json()
            if data and data.get('encrypted'):
                decrypted = openssl_decrypt(data['encrypted'])
                request._decrypted_data = json.loads(decrypted)
            else:
                request._decrypted_data = data
        except Exception as e:
            return jsonify({'error': 'Invalid encryption'}), 400

# ---- Admin check (plain JSON) ----
@app.route('/api/check_admin', methods=['POST'])
def check_admin():
    data = request._decrypted_data if hasattr(request, '_decrypted_data') else request.get_json()
    wallet = data.get('wallet') if data else None
    if not wallet:
        return jsonify({'admin': False}), 400
    is_admin = wallet.lower() == ADMIN_WALLET.lower()
    return jsonify({'admin': is_admin})

@app.route('/login')
def login():
    return redirect("https://github.com/login/oauth/authorize?client_id=" + os.getenv("GITHUB_CLIENT_ID"))

@app.route('/')
def home():
    return "Secure OAuth server running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
