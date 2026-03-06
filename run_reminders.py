from datetime import datetime
import os
from app import app
from models import db, Task, User, SMTPSettings
from services.brevo_email import send_email_from_db


def main():
    now = datetime.utcnow()

    with app.app_context():
        tasks = (
            Task.query
            .filter(Task.remind_email.is_(True))
            .filter(Task.remind_at.isnot(None))
            .filter(Task.remind_at <= now)
            .filter(Task.reminder_sent_at.is_(None))
            .filter(Task.done.is_(False))
            .all()
        )

        for t in tasks:
            user = User.query.get(t.user_id)
            
            # Check for SMTP configuration 
            smtp_settings = SMTPSettings.query.first()
            if not smtp_settings or not (smtp_settings.smtp_host and smtp_settings.smtp_username):
                print("⚠️  SMTP not configured - skipping email reminders")
                break
            
            # Pentru test, folosesc TEST_EMAIL din .env sau smtp settings, altfel user.notification_email
            test_email = os.getenv("TEST_EMAIL") or smtp_settings.test_email
            email_address = test_email if test_email else (user.notification_email if user else None)
            
            if not email_address:
                print(f"⚠️  No email address for task '{t.title}' - skipping email")
                continue

            subject = "Task Reminder"
            content = f"Don't forget about your task: {t.title}\n\nDue: {t.due_at.strftime('%Y-%m-%d %H:%M') if t.due_at else 'No due date'}"
            try:
                mid = send_email_from_db(email_address, subject, content)
                print(f"📧 Email sent to {email_address}: {t.title}")
                
                t.reminder_sent_at = now
                t.brevo_message_id = mid
                db.session.add(t)
            except Exception as e:
                print(f"❌ Error sending email: {e}")

        db.session.commit()


if __name__ == "__main__":
    main()
