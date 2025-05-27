from flask import Flask, request, render_template, redirect, url_for, flash
from collections import deque
from markupsafe import escape
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

messages = deque(maxlen=100)

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

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)