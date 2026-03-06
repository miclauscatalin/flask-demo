import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_from_db(to_email: str, subject: str, content: str, is_html: bool = False) -> str:
    """Trimit email folosind credentialele SMTP stocate in baza de date.
    / I send an email using the SMTP credentials stored in the database.
    Daca is_html=True, content este folosit direct ca corp HTML.
    / If is_html=True, content is used directly as the HTML body."""
    from models import SMTPSettings
    
    settings = SMTPSettings.query.first()
    if not settings or not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
        raise RuntimeError("SMTP settings not configured in database")

    try:
        # Construiesc mesajul email cu parti text si HTML
        # / I build the email message with both plain-text and HTML parts
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.sender_name} <{settings.sender_email}>"
        msg['To'] = to_email

        if is_html:
            # Content este deja HTML complet / Content is already full HTML
            import re
            plain_fallback = re.sub(r'<[^>]+>', '', content).strip()
            part1 = MIMEText(plain_fallback or content, 'plain')
            part2 = MIMEText(content, 'html')
        else:
            # Construiesc HTML simplu din text / I build simple HTML from plain text
            plain_fallback = content
            html_content = f"<html><body><p>{content.replace(chr(10), '<br>')}</p></body></html>"
            part1 = MIMEText(plain_fallback, 'plain')
            part2 = MIMEText(html_content, 'html')

        msg.attach(part1)
        msg.attach(part2)
        
        # Mă conectez la serverul SMTP, autentific şi trimit mesajul
        # / I connect to the SMTP server, authenticate, and send the message
        port = settings.smtp_port or 587
        server = smtplib.SMTP(settings.smtp_host, port)
        server.starttls()  # Folosesc TLS / Use TLS encryption
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.sender_email, to_email, msg.as_string())
        server.quit()
        
        return f"email-sent-to-{to_email}"
        
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("SMTP Authentication failed - check username and password")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"SMTP error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error sending email: {str(e)}")