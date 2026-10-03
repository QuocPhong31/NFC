import re
import secrets
import unicodedata


def generate_slug(name):

    name = unicodedata.normalize(
        "NFKD",
        name
    )

    name = "".join(
        c for c in name
        if not unicodedata.combining(c)
    )

    name = name.lower()

    name = name.replace(
        "đ",
        "d"
    )

    name = re.sub(
        r"[^a-z0-9\s-]",
        "",
        name
    )

    name = re.sub(
        r"[\s-]+",
        "-",
        name
    )

    name = name.strip("-")

    random_code = secrets.token_hex(3)

    return (
        f"{name}-{random_code}"
    )