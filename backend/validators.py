"""Validator Module"""
import re


def validate(data, regex):
    """Custom Validator"""
    return True if re.match(regex, data) else False


def validate_password(password: str):
    """Password Validator"""
    reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
    return validate(password, reg)


def validate_email(email: str):
    """Email Validator"""
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return validate(email, regex)


def validate_user(**kwargs):
    """User Validator"""
    if not kwargs.get('email') or not kwargs.get('password') or not kwargs.get('first_name'):
        return {
            'email': 'Email is required',
            'password': 'Password is required',
            'first_name': 'First Name is required.'
        }
    if not isinstance(kwargs.get('email'), str) or not isinstance(kwargs.get('password'), str):
        return {
            'email': 'Email must be a string',
            'password': 'Password must be a string',
        }
    if not validate_email(kwargs.get('email')):
        return {
            'email': 'Email is invalid'
        }
    if not validate_password(kwargs.get('password')):
        return {
            'password': 'Password is invalid, Should be at least 8 characters with \
                upper and lower case letters, numbers and special characters (e.g. @)'
        }
    return True
