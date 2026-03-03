import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_from_db(to_email: str, subject: str, content: str) -> str:
    """Send email using SMTP credentials from database"""
    from models import SMTPSettings
    
    settings = SMTPSettings.query.first()
    if not settings or not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
        raise RuntimeError("SMTP settings not configured in database")

    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.sender_name} <{settings.sender_email}>"
        msg['To'] = to_email
        
        # Add plain text part
        part1 = MIMEText(content, 'plain')
        msg.attach(part1)
        
        # Add HTML part
        html_content = f"""
        <html>
            <body>
                <p>{content.replace(chr(10), '<br>')}</p>
            </body>
        </html>
        """
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Connect to SMTP server and send
        port = settings.smtp_port or 587
        server = smtplib.SMTP(settings.smtp_host, port)
        server.starttls()  # Use TLS encryption
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