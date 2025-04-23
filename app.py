from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecret"

MAX_PLAYERS = 22
PASSWORD = "welcome123"

# Stores players by event date
player_lists = {}
current_event_date = str(date.today())

def get_lists():
    global current_event_date
    if current_event_date not in player_lists:
        player_lists[current_event_date] = {"main": [], "wait": []}
    return player_lists[current_event_date]

@app.route("/", methods=["GET", "POST"])
def index():
    lists = get_lists()
    if request.method == "POST":
        name = request.form["name"]
        friend = request.form.get("friend", "")
        players = [name] if not friend else [name, friend]

        lists["main"] = [p for p in lists["main"] if p not in players]
        lists["wait"] = [p for p in lists["wait"] if p not in players]

        for p in players:
            if len(lists["main"]) < MAX_PLAYERS:
                lists["main"].append(p)
            else:
                lists["wait"].append(p)

        return redirect(url_for("index"))

    return render_template("index.html", date=current_event_date, main=lists["main"], wait=lists["wait"])

@app.route("/remove", methods=["POST"])
def remove():
    name = request.form["name"]
    lists = get_lists()

    if name in lists["main"]:
        lists["main"].remove(name)
        while len(lists["main"]) < MAX_PLAYERS and lists["wait"]:
            promoted = lists["wait"].pop(0)
            lists["main"].append(promoted)
    elif name in lists["wait"]:
        lists["wait"].remove(name)

    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    global current_event_date

    if request.method == "POST":
        password = request.form["password"]
        new_date = request.form["date"]

        if password == PASSWORD:
            current_event_date = new_date
            return redirect(url_for("index"))
        else:
            return render_template("admin.html", error="Wrong password!")

    return render_template("admin.html", error="")

if __name__ == "__main__":
    app.run(debug=True)