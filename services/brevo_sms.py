import os
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER = os.getenv("BREVO_SENDER", "TaskDemo")

def send_sms(recipient_e164: str, content: str) -> str:
    if not BREVO_API_KEY:
        raise RuntimeError("BREVO_API_KEY missing")

    url = "https://api.brevo.com/v3/transactionalSMS/send"
    payload = {
        "sender": BREVO_SENDER,
        "recipient": recipient_e164,
        "content": content,
        "type": "transactional",
    }
    headers = {"api-key": BREVO_API_KEY, "Content-Type": "application/json", "accept": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    return str(data.get("messageId", ""))