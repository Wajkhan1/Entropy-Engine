from config import CRACK_SPEEDS


def get_crack_speed(algorithm: str) -> float:
    algorithm = algorithm.lower()

    if algorithm not in CRACK_SPEEDS:
        raise ValueError("Unsupported algorithm")

    return CRACK_SPEEDS[algorithm]


def estimate_crack_time(combinations: int, algorithm: str) -> float:
    speed = get_crack_speed(algorithm)
    return combinations / speed


def format_time(seconds: float) -> dict:
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    years = int(seconds // (60 * 60 * 24 * 365))

    return {
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "days": days,
        "years": years
    }