import requests
from CTFd.utils import get_app_config, get_config
from CTFd.utils.email.providers import EmailProvider


class BrevoEmailProvider(EmailProvider):
    @staticmethod
    def sendmail(addr, text, subject):
        sender_name = (
            get_config("mail_sender_name")
            or get_app_config("MAIL_SENDER_NAME")
            or os.getenv("MAIL_SENDER_NAME")
            or "XploitX 2.0 BETA"
        )
        mailfrom_addr = (
            get_config("mailfrom_addr")
            or get_app_config("MAILFROM_ADDR")
            or "xploitx2.0beta@gmail.com"
        )
        api_key = (
            get_config("brevo_api_key")
            or get_app_config("BREVO_API_KEY")
            or os.getenv("BREVO_API_KEY")
        )

        if not api_key:
            return False, "Brevo API key is not configured"

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        }

        payload = {
            "sender": {
                "name": sender_name,
                "email": mailfrom_addr,
            },
            "to": [
                {"email": addr}
            ],
            "subject": subject,
            "textContent": text,
        }

        try:
            r = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers=headers,
                json=payload,
                timeout=10.0,
            )
        except requests.RequestException as e:
            return (
                False,
                f"{type(e).__name__} exception occurred while handling your request",
            )

        if r.status_code in (200, 201, 202):
            return True, "Email sent"
        else:
            try:
                err_data = r.json()
                msg = err_data.get("message", r.text)
            except Exception:
                msg = r.text
            return False, f"Brevo error: {msg}"
