"""
Scheduler background pentru trimitere memento-uri.
/ Background scheduler for sending task reminders.
Folosesc APScheduler pentru a verifica mementourile la fiecare minut.
/ I use APScheduler to check reminders every minute.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from models import db, Task, User, SMTPSettings
from services.brevo_email import send_email_from_db


def check_and_send_reminders(app):
    """Verific sarcinile cu memento şi trimit emailuri dacă e cazul.
    / I check tasks with pending reminders and send emails if due."""
    with app.app_context():
        now = datetime.now()  # Folosesc ora locală a sistemului / I use local system time

        # Găsesc sarcinile care necesită memento — netrimiş, neterminat, cu dată trecută
        # / I fetch tasks that need a reminder: unsent, not done, remind_at in the past
        try:
            tasks = (
                Task.query
                .filter(Task.remind_email.is_(True))
                .filter(Task.remind_at.isnot(None))
                .filter(Task.remind_at <= now)
                .filter(Task.reminder_sent_at.is_(None))
                .filter(Task.done.is_(False))
                .all()
            )
        except Exception as e:
            # Tabelele pot lipsi la primul start / Tables may be missing on first start
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  DB not ready yet: {e}")
            return
        
        if not tasks:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No pending reminders")
            return
        
        # Verific configurația SMTP înainte să trimit
        # / I check SMTP configuration before sending
        smtp_settings = SMTPSettings.query.first()
        if not smtp_settings or not (smtp_settings.smtp_host and smtp_settings.smtp_username):
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  SMTP not configured - {len(tasks)} reminder(s) pending")
            return
        
        # Trimit mementourile către fiecare utilizator eligibil
        # / I send reminders to each eligible user
        for t in tasks:
            user = User.query.get(t.user_id)
            
            # Trimit direct pe emailul userului (fara override test)
            # / I send directly to the user's own notification_email (no test override)
            email_address = user.notification_email if user else None

            if not email_address:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  No email for task '{t.title}' - skipping")
                continue

            APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")
            task_url = f"{APP_BASE_URL}/tasks/{t.id}/view"
            username = user.username if user else "utilizator"
            lang = getattr(user, 'preferred_lang', 'ro')  # 'ro' sau 'en' / preferred language

            # Textele bilingve RO / EN / Bilingual strings RO / EN
            if lang == 'en':
                due_str     = t.due_at.strftime("%b %d, %Y at %H:%M") if t.due_at else "No due date"
                subject     = f"📌 Reminder: {t.title}"
                header_lbl  = "Task Reminder"
                greeting    = f"Hi, <strong style='color:#0f1117;'>{username}</strong>!"
                intro       = "You have a task that needs your attention:"
                due_label   = "Due:"
                btn_label   = "Open task"
                redirect_note = "If you are not logged in, you will be redirected to the login page first."
                footer_note = "Task Tracker &mdash; automated notification. Do not reply."
            else:
                due_str     = t.due_at.strftime("%d %b %Y, %H:%M") if t.due_at else "Fara data"
                subject     = f"📌 Memento: {t.title}"
                header_lbl  = "Memento sarcina"
                greeting    = f"Buna, <strong style='color:#0f1117;'>{username}</strong>!"
                intro       = "Ai o sarcina care necesita atentia ta:"
                due_label   = "Scadenta:"
                btn_label   = "Deschide sarcina"
                redirect_note = "Daca nu esti autentificat, vei fi redirectat catre login inainte de a vedea sarcina."
                footer_note = "Task Tracker &mdash; notificare automata. Nu raspunde la acest email."

            html_body = f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f0f4ff;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4ff;padding:32px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0"
       style="background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 24px rgba(67,97,238,.12);max-width:96vw;">
  <tr><td style="background:linear-gradient(135deg,#4361ee,#7c3aed);padding:28px 32px;">
    <p style="margin:0;font-size:11px;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.1em;">Task Tracker</p>
    <h1 style="margin:8px 0 0;font-size:22px;color:#fff;font-weight:800;">{header_lbl}</h1>
  </td></tr>
  <tr><td style="padding:28px 32px;">
    <p style="margin:0 0 6px;font-size:13px;color:#6b7280;">{greeting}</p>
    <p style="margin:0 0 20px;font-size:14px;color:#374151;">{intro}</p>
    <div style="background:#f0f4ff;border-left:4px solid #4361ee;border-radius:0 8px 8px 0;padding:16px 20px;margin-bottom:24px;">
      <p style="margin:0 0 6px;font-size:18px;font-weight:700;color:#0f1117;">{t.title}</p>
      <p style="margin:0;font-size:12px;color:#6b7280;">{due_label} <strong>{due_str}</strong></p>
    </div>
    <a href="{task_url}"
       style="display:inline-block;background:#4361ee;color:#fff;text-decoration:none;
              font-weight:700;font-size:14px;padding:12px 28px;border-radius:8px;
              box-shadow:0 3px 12px rgba(67,97,238,.35);">
      {btn_label} &rarr;
    </a>
    <p style="margin:24px 0 0;font-size:12px;color:#9ca3af;">{redirect_note}</p>
  </td></tr>
  <tr><td style="background:#f6f8ff;padding:16px 32px;border-top:1px solid #e5e9f5;">
    <p style="margin:0;font-size:11px;color:#9ca3af;">{footer_note}</p>
    <p style="margin:4px 0 0;font-size:10px;color:#c0c9e5;">Dev MiclausCatalin &middot; miclaus.catalin@gmail.com</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""

            try:
                mid = send_email_from_db(email_address, subject, html_body, is_html=True)
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 📧 Email sent to {email_address}: {t.title}")
                
                # Marchez sarcina ca trimisă pentru a nu mai trimite din nou
                # / I mark the task as sent so I don't send it again
                t.reminder_sent_at = now
                t.brevo_message_id = mid
                db.session.add(t)
            except Exception as e:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error sending email: {e}")
        
        db.session.commit()


def init_scheduler(app):
    """Inițializez şi pornesc scheduler-ul background.
    / I initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    
    # Adăug job-ul de verificare la interval de 1 minut
    # / I add the reminder-check job to run every minute
    scheduler.add_job(
        func=lambda: check_and_send_reminders(app),
        trigger="interval",
        minutes=1,
        id='reminder_checker',
        name='Check and send task reminders',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Reminder scheduler started - checking every minute")
    
    return scheduler
