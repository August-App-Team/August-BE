import random
import string


def get_random_code(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def is_valid_code(code: str, length: int = 8) -> bool:
    return code.isalnum() and len(code) == length