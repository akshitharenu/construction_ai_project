from twilio.rest import Client
from config import settings

_twilio = None


def _get_client():
    global _twilio
    if _twilio is None:
        _twilio = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _twilio


def send_whatsapp_alert(to: str, message: str) -> None:
    client = _get_client()
    client.messages.create(
        from_=settings.twilio_whatsapp_from,
        to=f"whatsapp:{to}",
        body=message,
    )
    print(f"[ALERT] WhatsApp sent to {to}")


def send_critical_alert(project_id: str, summary: str, action: str | None) -> None:
    body = f"CRITICAL — {project_id}\n\n{summary}"
    if action:
        body += f"\n\nAction needed: {action}"
    send_whatsapp_alert(settings.pm_whatsapp_number, body)
