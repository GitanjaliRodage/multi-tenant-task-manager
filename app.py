import utils.session
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)


# ---------------- MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    org_id = db.Column(db.String(50))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")
    deadline = db.Column(db.String(20))
    user = db.Column(db.String(50))
    org_id = db.Column(db.String(50))


# ---------------- AI PRIORITY ----------------
def ai_priority(text):
    text = text.lower()
    if "urgent" in text:
        return "High"
    elif "meeting" in text:
        return "Medium"
    elif "research" in text:
        return "Low"
    return "Medium"


# ---------------- LOGIN (NO METHOD ERROR) ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username, password=password
        ).first()

        if user:
            return redirect(f"/dashboard/{user.username}/{user.org_id}")
        else:
            return "Invalid Login"

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    org = request.form["org"]

    user = User(username=username, password=password, org_id=org)
    db.session.add(user)
    db.session.commit()

    return redirect("/")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard/<user>/<org>")
def dashboard(user, org):
    tasks = Task.query.filter_by(org_id=org).all()

    total = len(tasks)
    completed = len([t for t in tasks if t.status == "Completed"])
    pending = len([t for t in tasks if t.status == "Pending"])
    high = len([t for t in tasks if t.priority == "High"])

    return render_template(
        "dashboard.html",
        tasks=tasks,
        user=user,
        org=org,
        total=total,
        completed=completed,
        pending=pending,
        high=high,
    )


# ---------------- ADD TASK ----------------
@app.route("/add_task", methods=["POST"])
def add_task():
    title = request.form["title"]
    deadline = request.form["deadline"]
    user = request.form["user"]
    org = request.form["org"]

    priority = ai_priority(title)

    task = Task(
        title=title,
        priority=priority,
        deadline=deadline,
        user=user,
        org_id=org,
    )

    db.session.add(task)
    db.session.commit()

    return redirect(f"/dashboard/{user}/{org}")


# ---------------- COMPLETE TASK ----------------
@app.route("/complete/<int:id>/<user>/<org>")
def complete(id, user, org):
    task = Task.query.get(id)
    task.status = "Completed"
    db.session.commit()

    return redirect(f"/dashboard/{user}/{org}")


@app.route("/logout")
def logout():
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)