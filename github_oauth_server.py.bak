#!/usr/bin/env python3
import os, requests, json, subprocess, time
from flask import Flask, request, redirect, session, jsonify
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:5000/callback"
ADMIN_USERNAME = "jvoidial"

# ---- Connection log ----
CONNECTION_LOG = "connected_wallets.json"

def log_connection(wallet):
    if not wallet:
        return
    data = []
    if os.path.exists(CONNECTION_LOG):
        with open(CONNECTION_LOG, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    # Avoid duplicates for the same wallet (update timestamp)
    existing = next((item for item in data if item["wallet"].lower() == wallet.lower()), None)
    if existing:
        existing["last_seen"] = time.time()
    else:
        data.append({"wallet": wallet, "first_seen": time.time(), "last_seen": time.time()})
    with open(CONNECTION_LOG, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return "OAuth server running."

@app.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read:user"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400
    resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )
    token_data = resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return f"OAuth error: {token_data}", 400
    user = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    if user.get("login") == ADMIN_USERNAME:
        session["admin"] = True
        session["username"] = user["login"]
        return redirect("http://127.0.0.1:8000/index.html?auth=success")
    return f"Access denied. You are {user.get('login')}", 403

@app.route("/api/me")
def me():
    if session.get("admin"):
        return jsonify({"admin": True, "username": session.get("username")})
    return jsonify({"admin": False}), 401

@app.route("/api/seize", methods=["POST"])
def seize():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    subprocess.Popen(["python3", "scammer_monitor.py"])
    return jsonify({"status": "Seize triggered!"})

# ---- NEW: Log wallet connection ----
@app.route("/api/log_connection", methods=["POST"])
def log_wallet():
    data = request.get_json()
    wallet = data.get("wallet")
    if wallet:
        log_connection(wallet)
        return jsonify({"status": "logged"}), 200
    return jsonify({"error": "No wallet"}), 400

# ---- NEW: Admin view of connections ----
@app.route("/admin/connections")
def view_connections():
    if not session.get("admin"):
        return "Unauthorized", 401
    if not os.path.exists(CONNECTION_LOG):
        return "No connections logged yet."
    with open(CONNECTION_LOG, "r") as f:
        data = json.load(f)
    # Format as HTML
    html = "<h1>Connected Wallets</h1><ul>"
    for item in sorted(data, key=lambda x: x["last_seen"], reverse=True):
        html += f"<li>{item['wallet']} – last seen: {time.ctime(item['last_seen'])}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
