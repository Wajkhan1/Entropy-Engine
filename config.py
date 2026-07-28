
CRACK_SPEEDS = {
    "md5": 1e11,        # very fast (legacy)
    "sha256": 5e10,     # fast
    "bcrypt": 1000      # intentionally slow
}

MAX_PASSWORD_LENGTH = 128

ENTROPY_THRESHOLDS = {
    "weak": 40,
    "medium": 60,
    "strong": 80
}

COMMON_PASSWORDS_FILE = "data/common_passwords.txt"