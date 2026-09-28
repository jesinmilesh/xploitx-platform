import os
import secrets

from CTFd.cache import cache
from CTFd.exceptions.email import (
    UserConfirmTokenInvalidException,
    UserResetPasswordTokenInvalidException,
)
from CTFd.utils.encoding import hexencode


def generate_email_confirm_token(addr, timeout=1800):
    nonce = hexencode(os.urandom(32))
    otp = f"{secrets.randbelow(900000) + 100000}"
    cache.set(f"confirm_email_{nonce}", addr, timeout=timeout)
    cache.set(f"confirm_email_otp_{otp}", (addr, nonce), timeout=600)
    cache.set(f"confirm_email_nonce_otp_{nonce}", otp, timeout=timeout)
    return nonce


def get_otp_for_confirm_token(nonce):
    return cache.get(f"confirm_email_nonce_otp_{nonce}")


def verify_email_confirm_token(token_or_otp):
    # Check if 6 digit OTP was submitted
    token_str = str(token_or_otp).strip()
    if token_str.isdigit() and len(token_str) == 6:
        data = cache.get(f"confirm_email_otp_{token_str}")
        if data is None:
            raise UserConfirmTokenInvalidException
        addr, nonce = data
        return addr

    addr = cache.get(f"confirm_email_{token_str}")
    if addr is None:
        raise UserConfirmTokenInvalidException
    return addr


def remove_email_confirm_token(token_or_otp):
    token_str = str(token_or_otp).strip()
    if token_str.isdigit() and len(token_str) == 6:
        data = cache.get(f"confirm_email_otp_{token_str}")
        if data:
            addr, nonce = data
            cache.delete(f"confirm_email_{nonce}")
            cache.delete(f"confirm_email_nonce_otp_{nonce}")
            cache.delete(f"confirm_email_otp_{token_str}")
            return
    else:
        otp = cache.get(f"confirm_email_nonce_otp_{token_str}")
        if otp:
            cache.delete(f"confirm_email_otp_{otp}")
        cache.delete(f"confirm_email_nonce_otp_{token_str}")
        cache.delete(f"confirm_email_{token_str}")


def generate_password_reset_token(addr, timeout=1800):
    nonce = hexencode(os.urandom(32))
    cache.set(f"reset_password_{nonce}", addr, timeout=timeout)
    return nonce


def verify_reset_password_token(nonce):
    addr = cache.get(f"reset_password_{nonce}")
    if addr is None:
        raise UserResetPasswordTokenInvalidException
    return addr


def remove_reset_password_token(nonce):
    cache.delete(f"reset_password_{nonce}")
