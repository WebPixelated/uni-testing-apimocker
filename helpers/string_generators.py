import random
import string


def random_name(length: int) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def random_username(length: int) -> str:
    pool = string.ascii_letters + string.digits + "_"
    return "".join(random.choices(pool, k=length))


def random_email_local(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
