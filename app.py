from flask import Flask, render_template, redirect, url_for, flash, abort, Response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Task, SMTPSettings
from forms import RegisterForm, LoginForm, TaskForm, ProfileForm, SMTPForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash("Username already exists. Choose another.", "error")
            return render_template("register.html", form=form)

        user = User(username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Account created. You can now login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("tasks"))

        flash("Invalid username or password.", "error")

    return render_template("login.html", form=form)


@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/test-smtp", methods=["POST"])
@login_required
def test_smtp():
    try:
        settings = SMTPSettings.query.first()
        if not settings or not (settings.smtp_host and settings.smtp_username):
            return jsonify({"success": False, "error": "SMTP not configured"})
        
        from services.brevo_email import send_email_from_db
        test_email = settings.test_email or current_user.notification_email
        
        if not test_email:
            return jsonify({"success": False, "error": "No test email configured"})
        
        message_id = send_email_from_db(
            test_email, 
            "SMTP Test - Task Demo", 
            "This is a test email from your Task Demo app. SMTP is working correctly!"
        )
        
        return jsonify({"success": True, "message_id": message_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/smtp", methods=["GET", "POST"])
@login_required
def smtp_settings():
    # Get or create SMTP settings (global for app)
    settings = SMTPSettings.query.first()
    if not settings:
        settings = SMTPSettings()
    
    form = SMTPForm()
    
    if form.validate_on_submit():
        settings.smtp_host = form.smtp_host.data
        try:
            settings.smtp_port = int(form.smtp_port.data) if form.smtp_port.data else 587
        except:
            settings.smtp_port = 587
        settings.smtp_username = form.smtp_username.data
        settings.smtp_password = form.smtp_password.data
        settings.sender_email = form.sender_email.data or "noreply@example.com"
        settings.sender_name = form.sender_name.data or "Task Demo"
        settings.test_email = form.test_email.data
        
        if not settings.id:  # New record
            db.session.add(settings)
        db.session.commit()
        
        flash("SMTP settings saved successfully!", "success")
        return redirect(url_for("smtp_settings"))
    
    # Pre-populate form with current values
    form.smtp_host.data = settings.smtp_host
    form.smtp_port.data = str(settings.smtp_port) if settings.smtp_port else "587"
    form.smtp_username.data = settings.smtp_username
    form.smtp_password.data = settings.smtp_password
    form.sender_email.data = settings.sender_email
    form.sender_name.data = settings.sender_name
    form.test_email.data = settings.test_email
    
    return render_template("smtp.html", form=form, settings=settings)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.notification_email = form.notification_email.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
        
    # Pre-populate form with current values
    form.notification_email.data = current_user.notification_email
    
    return render_template("profile.html", form=form)


@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    form = TaskForm()

    if form.validate_on_submit():
        t = Task(
            title=form.title.data,
            owner=current_user,
            due_at=form.due_at.data,
            remind_at=form.remind_at.data,
            remind_email=bool(form.remind_email.data),
        )
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("tasks"))

    items = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )

    total = len(items)
    done_count = sum(1 for t in items if t.done)
    open_count = total - done_count
    progress = int((done_count / total) * 100) if total else 0

    return render_template(
        "tasks.html",
        form=form,
        tasks=items,
        total=total,
        done_count=done_count,
        open_count=open_count,
        progress=progress,
    )


@app.get("/tasks/<int:task_id>/ics")
@login_required

def task_ics(task_id: int):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)

    # dacă nu are due_at, punem default +1h de la creare
    start = task.due_at or task.created_at
    end = start  # event scurt (poți pune start+30min)

    def fmt(dt):
        # iCalendar UTC format (naiv -> tratăm ca UTC pentru demo)
        return dt.strftime("%Y%m%dT%H%M%SZ")

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Flask Task Tracker//EN
BEGIN:VEVENT
UID:task-{task.id}@flask-demo
DTSTAMP:{fmt(task.created_at)}
DTSTART:{fmt(start)}
DTEND:{fmt(end)}
SUMMARY:{task.title}
DESCRIPTION:Task from Flask demo app
END:VEVENT
END:VCALENDAR
"""
    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="task_{task.id}.ics"'},
    )


@app.get("/tasks/<int:task_id>/toggle")
@login_required
def toggle_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)

    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks"))


@app.get("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks"))


if __name__ == "__main__":
    app.run(debug=True)