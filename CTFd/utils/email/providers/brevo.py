import requests

from CTFd.utils import get_app_config, get_config
from CTFd.utils.email.providers import EmailProvider


class BrevoEmailProvider(EmailProvider):
    @staticmethod
    def sendmail(addr, text, subject):
        ctf_name = get_config("ctf_name") or "XploitX CTF"
        mailfrom_addr = (
            get_config("mailfrom_addr")
            or get_app_config("MAILFROM_ADDR")
            or "xploitx2.0beta@gmail.com"
        )
        api_key = (
            get_config("brevo_api_key")
            or get_app_config("BREVO_API_KEY")
            or get_config("mail_password")
            or get_app_config("MAIL_PASSWORD")
        )

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 CTFd/XploitX",
        }
        payload = {
            "sender": {"name": ctf_name, "email": mailfrom_addr},
            "to": [{"email": addr}],
            "subject": subject,
            "textContent": text,
        }

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=5.0)
            if r.status_code in (200, 201, 202):
                return True, "Email sent"
            else:
                return False, f"Brevo API error: {r.status_code} {r.text}"
        except requests.RequestException as e:
            return False, f"{type(e).__name__} occurred while sending email"
