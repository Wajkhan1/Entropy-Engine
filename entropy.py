import math
import string


def calculate_charset(password: str) -> int:
    charset = 0

    if any(c.islower() for c in password):
        charset += 26

    if any(c.isupper() for c in password):
        charset += 26

    if any(c.isdigit() for c in password):
        charset += 10

    if any(c in string.punctuation for c in password):
        charset += 32

    return charset


def calculate_entropy(password: str) -> float:
    charset = calculate_charset(password)

    if charset == 0:
        return 0

    return len(password) * math.log2(charset)


def total_combinations(password: str) -> int:
    charset = calculate_charset(password)
    return charset ** len(password)