from entropy import calculate_entropy, total_combinations
from hash_models import estimate_crack_time, format_time
from dictionary_checker import is_common_password
from password_generator import generate_secure_password

def has_sequential_chars(password: str):
    sequences = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"

    password_lower = password.lower()

    for i in range(len(password_lower) - 2):
        chunk = password_lower[i:i+3]
        if chunk in sequences or chunk in numbers:
            return True

    return False

def evaluate_strength(password: str, algorithm: str):

    if has_sequential_chars(password):
        return {
            "strength": "Weak",
            "reason": "Password contains sequential characters."
        }

    if is_common_password(password):
        return {
            "strength": "Weak",
            "reason": "Password found in common password list."
        }

    entropy = calculate_entropy(password)
    secure_password = generate_secure_password(16)
    combinations = total_combinations(password)
    seconds = estimate_crack_time(combinations, algorithm)
    formatted = format_time(seconds)

    years = formatted["years"]

    if years < 1:
        strength = "Weak"
    elif years < 100:
        strength = "Medium"
    elif years < 10000:
        strength = "Strong"
    else:
        strength = "Very Strong"

    return {
        "entropy_bits": round(entropy, 2),
        "strength": strength,
        "estimated_crack_time": formatted,
        "secure_password":secure_password
    }