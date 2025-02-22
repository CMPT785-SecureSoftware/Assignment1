# validation.py
import re

# ======================
# Validation Settings
# ======================

# Checking username for 6-20 characters, letters, digits, underscore, hyphen, period
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_.-]{6,20}$')

# Checking password for atleast one lowercase letter, one digit, and one special character.
def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    return re.fullmatch(pattern, password) is not None

def validate_input(username, password, check_username=True):
    if not username or not password:
        return "Username and password are required."
    if check_username:
        if not USERNAME_REGEX.match(username):
            return ("Invalid username. Must be 6-20 characters and contain only letters, numbers, underscores, "
                    "hyphens, or dots.")
    if not is_valid_password(password):
        return ("Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, "
                "one digit, and one special character.")
    # Checks if the password does not contain the username (case-insensitive)
    if username.lower() in password.lower():
        return "Password should not contain the username."
    # Returns none when both username and password meets requirements.
    return None
