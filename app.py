import os
import secrets
import datetime
import functools
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, abort, Response, jsonify, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Task, SMTPSettings
from forms import (
    RegisterForm, LoginForm, TaskForm, TaskEditForm, ProfileForm, SMTPForm,
    TwoFAForm, ForgotPasswordForm, ResetPasswordForm,
)
from scheduler import init_scheduler

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Creez tabelele automat dacă nu există (primul deploy, DB goală)
# / Auto-create all tables on startup if they don't exist (first deploy, empty DB)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Pornesc scheduler-ul pentru memento-urile prin email
# / I start the background scheduler for email reminders
scheduler = init_scheduler(app)

# Creez folderul de upload dacă nu există
# / I create the upload folder if it doesn't exist yet
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ── Creare automată admin la primul request ────────────────────────────
# / Auto-create admin on first request if credentials are set in .env
_admin_ready = False

@app.before_request
def _ensure_admin_exists():
    """Creez userul admin din .env o singură dată, la primul request.
    / I create the admin user from .env once, on the first request."""
    global _admin_ready
    if _admin_ready:
        return
    _admin_ready = True
    admin_user = os.getenv("ADMIN_USERNAME")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    if not admin_user or not admin_pass:
        return
    try:
        existing = User.query.filter_by(username=admin_user).first()
        if not existing:
            u = User(
                username=admin_user,
                notification_email=os.getenv("ADMIN_EMAIL") or None,
            )
            u.set_password(admin_pass)
            u.role = "admin"
            db.session.add(u)
            db.session.commit()
    except Exception:
        pass  # DB poate să nu existe încă / DB may not exist yet

ALLOWED_EXT = {"jpg", "jpeg", "png", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# Filtru Jinja2 pentru JSON parsing in templates / Jinja2 filter for JSON parsing in templates
import json as _json
@app.template_filter('from_json')
def from_json_filter(value):
    """Deserializez un string JSON in Python / Deserialize a JSON string to Python."""
    try:
        return _json.loads(value) if value else []
    except Exception:
        return []


def get_task_images(task) -> list:
    """Returneaza lista de fisiere imagine pentru un task (suporta multi + legacy).
    / Returns the list of image filenames for a task (supports multi + legacy single)."""
    import json
    if task.image_filenames:
        try:
            imgs = json.loads(task.image_filenames)
            return [f for f in imgs if f]
        except Exception:
            pass
    if task.image_filename:
        return [task.image_filename]
    return []

# ── Headere de securitate pe toate răspunsurile ──────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"]        = "SAMEORIGIN"
    response.headers["X-XSS-Protection"]       = "1; mode=block"
    response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"]      = "geolocation=(), microphone=(), camera=()"
    return response


def admin_required(f):
    """Decorator: blochez accesul dacă userul nu e admin.
    / Decorator: I block access if the user is not admin."""
    @functools.wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


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
        # Setez rolul implicit 'user' la inregistrare
        # / I set the default role 'user' on registration
        user.role = 'user'
        user.set_password(form.password.data)
        # Salvez emailul pentru 2FA / Save email for 2FA
        user.notification_email = form.email.data.strip().lower()

        db.session.add(user)
        db.session.commit()

        flash("Cont creat cu succes! Te poti autentifica.", "success")
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

            # Adminul sare peste 2FA / Admin bypasses 2FA
            if user.is_admin:
                login_user(user, remember=form.remember.data)
                return redirect(url_for("tasks"))

            # Verific ca userul are email pentru 2FA / Check user has email for 2FA
            if not user.notification_email:
                flash("Contul tau nu are o adresa de email setata. "
                      "Seteaz-o din sectiunea Profil.", "error")
                login_user(user, remember=form.remember.data)
                return redirect(url_for("profile"))

            # Generez şi trimit codul 2FA / Generate and send the 2FA code
            code = f"{secrets.randbelow(1_000_000):06d}"
            session['_2fa_uid']  = user.id
            session['_2fa_code'] = code
            session['_2fa_exp']  = (
                datetime.datetime.now() + datetime.timedelta(minutes=10)
            ).timestamp()
            session['_2fa_rem']  = bool(form.remember.data)

            try:
                from services.brevo_email import send_email_from_db
                _2fa_lang = getattr(user, 'preferred_lang', 'ro')
                _2fa_subj = "Cod 2FA – Task Tracker" if _2fa_lang == 'ro' else "2FA Code – Task Tracker"
                _2fa_html = f"""<!DOCTYPE html>
<html lang="{_2fa_lang}"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f0f4ff;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4ff;padding:32px 0;">
<tr><td align="center">
<table width="520" cellpadding="0" cellspacing="0"
       style="background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 24px rgba(67,97,238,.12);max-width:96vw;">
  <tr><td style="background:linear-gradient(135deg,#4361ee,#7c3aed);padding:24px 32px;">
    <p style="margin:0;font-size:11px;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.1em;">Task Tracker</p>
    <h1 style="margin:8px 0 0;font-size:20px;color:#fff;font-weight:800;">
      {'Autentificare in doi pasi' if _2fa_lang == 'ro' else 'Two-Factor Authentication'}
    </h1>
  </td></tr>
  <tr><td style="padding:28px 32px;">
    <p style="margin:0 0 16px;font-size:14px;color:#374151;">
      {'Buna' if _2fa_lang == 'ro' else 'Hi'}, <strong style="color:#0f1117;">{user.username}</strong>!
    </p>
    <p style="margin:0 0 20px;font-size:13px;color:#6b7280;">
      {'Codul tau de verificare este:' if _2fa_lang == 'ro' else 'Your verification code is:'}
    </p>
    <div style="background:#f0f4ff;border:2px solid #4361ee;border-radius:10px;
                padding:20px;text-align:center;margin-bottom:24px;">
      <span style="font-size:36px;font-weight:800;color:#4361ee;letter-spacing:10px;">{code}</span>
    </div>
    <p style="margin:0 0 8px;font-size:12px;color:#9ca3af;">
      {'Expiră în 10 minute.' if _2fa_lang == 'ro' else 'Expires in 10 minutes.'}
    </p>
    <p style="margin:0;font-size:12px;color:#9ca3af;">
      {'Dacă nu ai solicitat acest cod, ignoră acest mesaj.' if _2fa_lang == 'ro' else 'If you did not request this code, please ignore this email.'}
    </p>
  </td></tr>
  <tr><td style="background:#f6f8ff;padding:14px 32px;border-top:1px solid #e5e9f5;">
    <p style="margin:0;font-size:11px;color:#9ca3af;">Task Tracker &mdash;
      {'notificare automata. Nu raspunde la acest email.' if _2fa_lang == 'ro' else 'automated notification. Do not reply.'}
    </p>
    <p style="margin:4px 0 0;font-size:10px;color:#c0c9e5;">Dev MiclausCatalin &middot; miclaus.catalin@gmail.com</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""
                send_email_from_db(user.notification_email, _2fa_subj, _2fa_html, is_html=True)
            except Exception:
                # Curăț sesiunea la eśec / Clean session on failure
                for k in ('_2fa_uid', '_2fa_code', '_2fa_exp', '_2fa_rem'):
                    session.pop(k, None)
                flash("Nu am putut trimite codul 2FA. Verifică setările SMTP cu adminul.", "error")
                return render_template("login.html", form=form)

            return redirect(url_for("verify_2fa"))

        flash("Username sau parolă incorectă.", "error")

    return render_template("login.html", form=form)


@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    """Verific codul 2FA trimis pe email și autentific userul.
    / I verify the 2FA code sent by email and log the user in."""
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))
    if '_2fa_uid' not in session:
        return redirect(url_for("login"))

    form = TwoFAForm()
    if form.validate_on_submit():
        # Verific expirarea codului / Check code expiry
        if datetime.datetime.now().timestamp() > session.get('_2fa_exp', 0):
            for k in ('_2fa_uid', '_2fa_code', '_2fa_exp', '_2fa_rem'):
                session.pop(k, None)
            flash("Codul a expirat. Reîncearcă autentificarea.", "error")
            return redirect(url_for("login"))

        if form.code.data.strip() == session.get('_2fa_code'):
            user = User.query.get(session['_2fa_uid'])
            remember = session.pop('_2fa_rem', False)
            for k in ('_2fa_uid', '_2fa_code', '_2fa_exp'):
                session.pop(k, None)
            if user:
                login_user(user, remember=remember)
                return redirect(url_for("tasks"))

        flash("Cod incorect. Încearcă din nou.", "error")

    return render_template("verify_2fa.html", form=form)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Declanșez resetarea parolei prin trimiterea unui cod pe email.
    / I trigger password reset by sending a code to the user's email."""
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("Username inexistent.", "error")
            return render_template("forgot_password.html", form=form)

        if not user.notification_email:
            flash(
                "Acest cont nu are un email setat. "
                "Contactează adminul pentru resetare manuală.", "error"
            )
            return render_template("forgot_password.html", form=form)

        # Generez codul de resetare / Generate the reset code
        code = f"{secrets.randbelow(1_000_000):06d}"
        session['_reset_uid']  = user.id
        session['_reset_code'] = code
        session['_reset_exp']  = (
            datetime.datetime.now() + datetime.timedelta(minutes=15)
        ).timestamp()

        try:
            from services.brevo_email import send_email_from_db
            send_email_from_db(
                user.notification_email,
                "Resetare parolă – Task Tracker",
                f"Codul tău de resetare a parolei este: {code}\n"
                f"Expiră în 15 minute.\n\n"
                f"Dacă nu ai solicitat resetarea, ignoră acest mesaj."
            )
            flash("Codul de resetare a fost trimis pe email.", "success")
            return redirect(url_for("reset_password"))
        except Exception:
            for k in ('_reset_uid', '_reset_code', '_reset_exp'):
                session.pop(k, None)
            flash("Nu am putut trimite emailul. Verifică setările SMTP cu adminul.", "error")

    return render_template("forgot_password.html", form=form)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Resetez parola utilizatorului cu un cod valid primit pe email.
    / I reset the user's password using a valid code received by email."""
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))
    if '_reset_uid' not in session:
        return redirect(url_for("forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Verific expirarea / Check expiry
        if datetime.datetime.now().timestamp() > session.get('_reset_exp', 0):
            for k in ('_reset_uid', '_reset_code', '_reset_exp'):
                session.pop(k, None)
            flash("Codul a expirat. Reîncearcă.", "error")
            return redirect(url_for("forgot_password"))

        if form.code.data.strip() == session.get('_reset_code'):
            user = User.query.get(session['_reset_uid'])
            for k in ('_reset_uid', '_reset_code', '_reset_exp'):
                session.pop(k, None)
            if user:
                user.set_password(form.password.data)
                db.session.commit()
                flash("Parolă resetată cu succes! Te poți autentifica.", "success")
                return redirect(url_for("login"))

        flash("Cod incorect. Încearcă din nou.", "error")

    return render_template("reset_password.html", form=form)


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
    # Preiau sau creez setările SMTP globale
    # / I fetch or create the global SMTP settings record
    settings = SMTPSettings.query.first()
    if not settings:
        settings = SMTPSettings()

    form = SMTPForm()

    is_admin = current_user.is_admin

    # Doar adminul poate salva modificările
    # / Only admin is allowed to save changes
    if is_admin and form.validate_on_submit():
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

        if not settings.id:  # Înregistrare nouă / New record​
            db.session.add(settings)
        db.session.commit()

        flash("SMTP settings saved successfully!", "success")
        return redirect(url_for("smtp_settings"))

    # Dacă utilizatorul este admin, populez formularul cu valorile curente
    # / If admin, I populate the form with the current stored values
    if is_admin:
        form.smtp_host.data = settings.smtp_host
        form.smtp_port.data = str(settings.smtp_port) if settings.smtp_port else "587"
        form.smtp_username.data = settings.smtp_username
        form.smtp_password.data = settings.smtp_password
        form.sender_email.data = settings.sender_email
        form.sender_name.data = settings.sender_name
        form.test_email.data = settings.test_email

    # Dacă userul nu e admin, nu îi arăt valorile adminului — doar instrucțiuni
    # / If not admin, I hide the real values — show instructions only
    return render_template("smtp.html", form=form, settings=(settings if is_admin else None), is_admin=is_admin)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.notification_email = form.notification_email.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
        
    # Populez formularul cu emailul existent al utilizatorului
    # / I populate the form with the user's existing email
    form.notification_email.data = current_user.notification_email
    
    return render_template("profile.html", form=form)


@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    form = TaskForm()

    # Oblig utilizatorul să aibă email setat înainte să creeze sarcini
    # / Force the user to have notification_email set before creating tasks
    if not current_user.notification_email:
        flash("Completează-ți mai întâi adresa de email în Profil pentru a primi memento-uri.", "error")
        return redirect(url_for("profile"))

    if form.validate_on_submit():
        t = Task(
            title=form.title.data,
            owner=current_user,
            due_at=form.due_at.data,
            remind_at=form.remind_at.data,
            remind_email=bool(form.remind_email.data),
        )
        db.session.add(t)
        db.session.flush()  # Obtin ID-ul fara commit definitiv / Get the ID without final commit

        # Salvez preferinta de limba din UI / Save UI language preference
        lang = request.form.get('__lang', 'ro')
        if lang in ('ro', 'en') and current_user.preferred_lang != lang:
            current_user.preferred_lang = lang

        # Procesez pana la 5 imagini / Handle up to 5 uploaded images
        import json
        files = request.files.getlist('image')
        saved = []
        for f in files[:5]:
            if f and f.filename and allowed_file(f.filename):
                fname = secure_filename(f"task_{t.id}_{f.filename}")
                # Evit suprascrieri cu suffix unic / Avoid overwrites with unique suffix
                base, ext = os.path.splitext(fname)
                fname = f"{base}_{secrets.token_hex(4)}{ext}"
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
                saved.append(fname)
        if saved:
            t.image_filenames = json.dumps(saved)
            t.image_filename = saved[0]  # legacy compat

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

    # Dacă nu are `due_at`, folosesc `created_at` ca punkt de start al evenimentului
    # / If no due_at, I fall back to created_at as the event start
    start = task.due_at or task.created_at
    end = start  # eveniment scurt — pot seta start+30min dacă vreau

    def fmt(dt):
        # Formatez data pentru iCalendar (UTC naïv — suficient pentru demo)
        # / I format the datetime for iCalendar (naïve UTC — fine for demo)
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


@app.route("/tasks/<int:task_id>/remove-image", methods=["GET", "POST"])
@login_required
def remove_task_image(task_id: int):
    """Sterg o imagine specifica dupa filename din lista sarcinii.
    / I delete a specific image by filename from the task's image list."""
    import json
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    fname = request.args.get('f') or request.form.get('f')
    if fname:
        imgs = get_task_images(task)
        if fname in imgs:
            img_path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
            if os.path.exists(img_path):
                os.remove(img_path)
            imgs = [x for x in imgs if x != fname]
            task.image_filenames = json.dumps(imgs) if imgs else None
            task.image_filename = imgs[0] if imgs else None
            db.session.commit()
            flash("Imagine stearsa.", "success")
    return redirect(url_for("edit_task", task_id=task.id))


@app.get("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    # Sterg toate imaginile atasate de pe disc
    # / I delete all attached images from disk
    for fname in get_task_images(task):
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    # Userul poate edita doar sarcinile proprii; adminul poate edita orice
    # / The user can only edit their own tasks; admin can edit any
    if task.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = TaskEditForm()

    if form.validate_on_submit():
        task.title = form.title.data
        task.notes = form.notes.data
        task.due_at = form.due_at.data
        task.remind_at = form.remind_at.data
        task.remind_email = bool(form.remind_email.data)

        # Procesez imagini noi (max 5 total) / Handle new images (max 5 total)
        import json
        files = request.files.getlist('image')
        existing = get_task_images(task)
        new_saved = []
        slots_left = max(0, 5 - len(existing))
        for f in files[:slots_left]:
            if f and f.filename and allowed_file(f.filename):
                fname = secure_filename(f"task_{task.id}_{f.filename}")
                base, ext = os.path.splitext(fname)
                fname = f"{base}_{secrets.token_hex(4)}{ext}"
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
                new_saved.append(fname)
        if new_saved:
            combined = existing + new_saved
            task.image_filenames = json.dumps(combined)
            task.image_filename = combined[0]

        db.session.commit()
        flash("Task actualizat!", "success")
        return redirect(url_for("view_task", task_id=task.id))

    # Populez formularul cu datele curente ale sarcinii
    # / I populate the form with the task's current data
    form.title.data = task.title
    form.notes.data = task.notes
    form.due_at.data = task.due_at
    form.remind_at.data = task.remind_at
    form.remind_email.data = task.remind_email

    return render_template("task_edit.html", form=form, task=task,
                           task_images=get_task_images(task))


@app.get("/tasks/<int:task_id>/view")
@login_required
def view_task(task_id: int):
    """Afisez detaliile unui task (read-only). / I show task details (read-only)."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("task_view.html", task=task,
                           task_images=get_task_images(task),
                           now=datetime.datetime.now())


# ──────────────────────────────────────────
# Panou de administrare / Admin Panel
# ──────────────────────────────────────────

@app.get("/admin")
@admin_required
def admin_dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("admin.html", users=users, tasks=tasks)


@app.get("/admin/users/<int:user_id>/toggle-role")
@admin_required
def admin_toggle_role(user_id: int):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Nu îți poți schimba propriul rol.", "error")
        return redirect(url_for("admin_dashboard"))
    user.role = "user" if user.is_admin else "admin"
    db.session.commit()
    flash(f"Rolul lui {user.username} este acum '{user.role}'.", "success")
    return redirect(url_for("admin_dashboard"))


@app.get("/admin/users/<int:user_id>/delete")
@admin_required
def admin_delete_user(user_id: int):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Nu te poți șterge pe tine înșuți.", "error")
        return redirect(url_for("admin_dashboard"))
    db.session.delete(user)
    db.session.commit()
    flash(f"Utilizatorul '{user.username}' a fost șters.", "success")
    return redirect(url_for("admin_dashboard"))


@app.get("/admin/tasks/<int:task_id>/delete")
@admin_required
def admin_delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    if task.image_filename:
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], task.image_filename)
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(task)
    db.session.commit()
    flash("Task șters.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    # Nu rulеz cu debug=True în producție; controlez prin variabila FLASK_DEBUG
    # / I never run with debug=True in production; I control it via FLASK_DEBUG env var
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)