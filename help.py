
import re

def validate_password(password):
    if not password:
        raise ValueError("Password is not Provided. Please enter Password.")
    if not re.match('\d.*[A-Z]|[a-z].*\d',password):
        raise ValueError('Password must contain 1 capital letter and 1 number')
    if len(password) < 8 or len(password) > 50:
      raise ValueError('Password must be between 8 and 50 characters')


