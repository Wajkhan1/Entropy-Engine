from pathlib import Path
from config import COMMON_PASSWORDS_FILE

COMMON_PASSWORDS = set()


def load_common_passwords():
    global COMMON_PASSWORDS

    file_path = Path(COMMON_PASSWORDS_FILE)

    if not file_path.exists():
        print("Warning: common passwords file not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        COMMON_PASSWORDS = set(line.strip().lower() for line in f)


def is_common_password(password: str) -> bool:
    return password.lower() in COMMON_PASSWORDS