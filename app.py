from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "scanner_secret_key"

history = []


# LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":

            session["user"] = username
            return redirect(url_for("home"))

        else:

            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

    return render_template("login.html")


# HOME PAGE
@app.route("/home")
def home():

    if "user" not in session:
        return redirect(url_for("login"))

    safe_count = sum(1 for item in history if "Safe" in item["result"])
    danger_count = sum(1 for item in history if "Dangerous" in item["result"])
    suspicious_count = sum(1 for item in history if "Suspicious" in item["result"])

    return render_template(
        "index.html",
        username=session["user"],
        history=history,
        total=len(history),
        safe=safe_count,
        danger=danger_count,
        suspicious=suspicious_count
    )


# SCAN FILE
# SCAN FILE
@app.route("/scan", methods=["POST"])
def scan():

    if "user" not in session:
        return redirect(url_for("login"))

    file = request.files["file"]
    filename = file.filename.lower().strip()

    filesize = "Unknown"

    try:
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if size < 1024 * 1024:
            filesize = f"{round(size / 1024, 2)} KB"

        else:
            filesize = f"{round(size / (1024 * 1024), 2)} MB"

    except:
        pass

    scantime = "1.2 sec"

    dangerous_ext = [".exe", ".bat", ".cmd", ".msi", ".scr"]
    suspicious_ext = [".apk", ".zip", ".rar"]

    if any(filename.endswith(ext) for ext in dangerous_ext):

        result = "Dangerous File ❌"
        color = "red"
        risk = 100

    elif any(filename.endswith(ext) for ext in suspicious_ext):

        result = "Suspicious File ⚠️"
        color = "orange"
        risk = 50

    else:

        result = "Safe File ✅"
        color = "green"
        risk = 0

    time_now = datetime.now().strftime("%I:%M %p")

    history.insert(0, {
        "filename": filename,
        "result": result,
        "time": time_now
    })

    safe_count = sum(1 for item in history if "Safe" in item["result"])
    danger_count = sum(1 for item in history if "Dangerous" in item["result"])
    suspicious_count = sum(1 for item in history if "Suspicious" in item["result"])

    return render_template(
        "index.html",
        username=session["user"],
        result=result,
        color=color,
        risk=risk,
        filesize=filesize,
        scantime=scantime,
        history=history,
        total=len(history),
        safe=safe_count,
        danger=danger_count,
        suspicious=suspicious_count
    )
    # CLEAR HISTORY
@app.route("/clear")
def clear():

    global history

    history.clear()

    return redirect(url_for("home"))

# LOGOUT
@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)