import time
import os
from flask import Flask, request, render_template, redirect, \
    url_for, flash, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from collections import deque
from threading import Lock
from markupsafe import escape
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

announcements = ["This is an announcement. Announcements will always be official information from the developer. Don't trust anyone in chat who says they're developer without proof."]

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)

messages = deque(maxlen=100)

GLOBAL_REQUEST_LIMIT = 250
TIME_WINDOW = 60

request_times = []
lock = Lock()


@app.before_request
def limit_global_requests():
    now = time.time()
    with lock:
        # Remove timestamps older than TIME_WINDOW seconds
        while request_times and request_times[0] <= now - TIME_WINDOW:
            request_times.pop(0)

        if len(request_times) >= GLOBAL_REQUEST_LIMIT:
            # Deny access if over limit
            abort(429, description="Server busy, try again later")

        # Record this request
        request_times.append(now)


@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        msg = request.form.get("msg", "").strip()
        signature = request.form.get("signature", "").strip()

        # Basic validation
        if not username or not msg:
            flash("Username and message are required.")
        elif len(username) > 15:
            flash("Username must be at most 15 characters.")
        elif len(msg) > 2500:
            flash("Message must be at most 2500 characters.")
        elif len(signature) > 2000:
            flash("Signature is too long.")
        else:
            # Escape to prevent HTML injection
            safe_username = escape(username)
            safe_msg = escape(msg)
            safe_signature = escape(signature) if signature else None

            # Store the message with optional signature
            messages.appendleft({
                "username": safe_username,
                "msg": safe_msg,
                "signature": safe_signature
            })
            return redirect(url_for("chat"))

    return render_template("chat.html", messages=messages)


@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/announcements")
def announcements():
    return render_template("announcements.html")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
