"""This file contains multiple generator realated with the one-time-password application.

Functions:
    generate_otp_code: Generate an alphanumeric code.
"""
import random
import string as string_module


def generate_otp_code(length=8, custom_charset=""):
    """Generates a random 8-digit (or custom length) alphanumeric OTP string.

    Args:
        length (int, optional): The desired length of the OTP. Defaults to 8.
        custom_charset (string, optional): A string with chars that are used to generate the OTP code. If is a falsy
        value the otp code would be generated with
        ascii_letters + digits ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789').

    Returns:
        str: The generated OTP string.
    """
    allowed_chars = string_module.ascii_letters + string_module.digits
    allowed_chars = custom_charset if custom_charset else allowed_chars
    otp = ''.join(random.choice(allowed_chars) for _ in range(length))

    return otp
