from flask import url_for

from CTFd.constants.email import (
    DEFAULT_PASSWORD_CHANGE_ALERT_BODY,
    DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT,
    DEFAULT_PASSWORD_RESET_BODY,
    DEFAULT_PASSWORD_RESET_SUBJECT,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    DEFAULT_VERIFICATION_EMAIL_BODY,
    DEFAULT_VERIFICATION_EMAIL_SUBJECT,
)
from CTFd.models import Users
from CTFd.utils import get_config
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email.providers.brevo import BrevoEmailProvider
from CTFd.utils.email.providers.mailgun import MailgunEmailProvider
from CTFd.utils.email.providers.smtp import SMTPEmailProvider
from CTFd.utils.email.templates import (
    get_password_change_alert_email_html,
    get_password_reset_email_html,
    get_successful_registration_email_html,
    get_user_created_email_html,
    get_verification_email_html,
)
from CTFd.utils.formatters import safe_format
from CTFd.utils.security.email import (
    generate_email_confirm_token,
    generate_password_reset_token,
    get_otp_for_confirm_token,
)

PROVIDERS = {
    "smtp": SMTPEmailProvider,
    "mailgun": MailgunEmailProvider,
    "brevo": BrevoEmailProvider,
}


def sendmail(addr, text, subject="Message from {ctf_name}", html=None):
    subject = safe_format(subject, ctf_name=get_config("ctf_name"))
    provider = get_mail_provider()
    EmailProvider = PROVIDERS.get(provider)
    if EmailProvider is None:
        return False, "No mail settings configured"
    try:
        return EmailProvider.sendmail(addr, text, subject, html=html)
    except TypeError:
        return EmailProvider.sendmail(addr, text, subject)


def password_change_alert(email):
    reset_url = url_for("auth.reset_password", _external=True)
    user = Users.query.filter_by(email=email).first()
    user_name = user.name if user else "Operative"
    ctf_name = get_config("ctf_name") or "XPLOITX 2.0 BETA"

    subject = f"{ctf_name} - Security Alert: Password Changed"
    html = get_password_change_alert_email_html(
        name=user_name,
        reset_url=reset_url,
        ctf_name=ctf_name,
    )
    text = safe_format(
        get_config("password_change_alert_body") or DEFAULT_PASSWORD_CHANGE_ALERT_BODY,
        ctf_name=ctf_name,
        ctf_description=get_config("ctf_description"),
        url=reset_url,
    )
    return sendmail(addr=email, text=text, subject=subject, html=html)


def forgot_password(email):
    token = generate_password_reset_token(email)
    reset_url = url_for("auth.reset_password", data=token, _external=True)
    user = Users.query.filter_by(email=email).first()
    user_name = user.name if user else "Operative"
    ctf_name = get_config("ctf_name") or "XPLOITX 2.0 BETA"

    subject = f"{ctf_name} - Password Reset Request"
    html = get_password_reset_email_html(
        name=user_name,
        reset_url=reset_url,
        ctf_name=ctf_name,
    )
    text = safe_format(
        get_config("password_reset_body") or DEFAULT_PASSWORD_RESET_BODY,
        ctf_name=ctf_name,
        ctf_description=get_config("ctf_description"),
        url=reset_url,
    )
    return sendmail(addr=email, text=text, subject=subject, html=html)


def verify_email_address(addr):
    token = generate_email_confirm_token(addr)
    otp = get_otp_for_confirm_token(token) or "780808"
    confirm_url = url_for(
        "auth.confirm",
        data=token,
        _external=True,
        _method="GET",
    )
    user = Users.query.filter_by(email=addr).first()
    user_name = user.name if user else "Operative"
    ctf_name = get_config("ctf_name") or "XPLOITX 2.0 BETA"

    subject = f"{ctf_name} - Verification Code"
    html = get_verification_email_html(
        name=user_name,
        otp=otp,
        confirm_url=confirm_url,
        ctf_name=ctf_name,
    )
    text = f"""PRATHYUSHA ENGINEERING COLLEGE
(AN AUTONOMOUS INSTITUTION)
DEPARTMENT OF CYBER SECURITY
{ctf_name}

Verification Code

Dear {user_name},

Your one-time verification code for registering in {ctf_name} is:

{otp}

This OTP is valid for 10 minutes. Please enter this code on the registration page to complete your email verification.
Direct link: {confirm_url}

If you did not request this email, please ignore this message.
"""
    return sendmail(addr=addr, text=text, subject=subject, html=html)


def successful_registration_notification(addr):
    arena_url = url_for("views.static_html", _external=True)
    user = Users.query.filter_by(email=addr).first()
    user_name = user.name if user else "Operative"
    ctf_name = get_config("ctf_name") or "XPLOITX 2.0 BETA"

    subject = f"{ctf_name} - Registration Confirmed"
    html = get_successful_registration_email_html(
        name=user_name,
        url=arena_url,
        ctf_name=ctf_name,
    )
    text = safe_format(
        get_config("successful_registration_email_body")
        or DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
        ctf_name=ctf_name,
        ctf_description=get_config("ctf_description"),
        url=arena_url,
    )
    return sendmail(addr=addr, text=text, subject=subject, html=html)


def user_created_notification(addr, name, password):
    login_url = url_for("auth.login", _external=True)
    ctf_name = get_config("ctf_name") or "XPLOITX 2.0 BETA"

    subject = f"{ctf_name} - Account Credentials"
    html = get_user_created_email_html(
        name=name,
        password=password,
        url=login_url,
        ctf_name=ctf_name,
    )
    text = safe_format(
        get_config("user_creation_email_body") or DEFAULT_USER_CREATION_EMAIL_BODY,
        ctf_name=ctf_name,
        ctf_description=get_config("ctf_description"),
        url=login_url,
        name=name,
        password=password,
    )
    return sendmail(addr=addr, text=text, subject=subject, html=html)


def check_email_is_whitelisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_whitelist = get_config("domain_whitelist")

    if domain_whitelist:
        domain_whitelist = [d.strip() for d in domain_whitelist.split(",")]

        for allowed_domain in domain_whitelist:
            if allowed_domain.startswith("*."):
                # domains should never container the "*" char
                if "*" in domain:
                    return False

                # Handle wildcard domain case
                suffix = allowed_domain[1:]  # Remove the "*" prefix
                if domain.endswith(suffix):
                    return True

            elif domain == allowed_domain:
                return True

        # whitelist is specified but the email doesn't match any domains
        return False

    # whitelist is not specified - allow all emails
    return True


def check_email_is_blacklisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_blacklist = get_config("domain_blacklist")

    if domain_blacklist:
        domain_blacklist = [d.strip() for d in domain_blacklist.split(",")]

        for disallowed_domain in domain_blacklist:
            if disallowed_domain.startswith("*."):
                # domains should never container the "*" char
                if "*" in domain:
                    return True

                # Handle wildcard domain case
                suffix = disallowed_domain[1:]  # Remove the "*" prefix
                if domain.endswith(suffix):
                    return True

            elif domain == disallowed_domain:
                return True

        # blacklist is specified but the email is not blacklisted
        return False

    # blacklist is not specified - no emails are blacklisted
    return False
