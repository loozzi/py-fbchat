import json
import random
import string
from typing import Any, Mapping

import requests


def session_factory():
    return requests.Session()


def prefix_url(url: str) -> str:
    if url.startswith("/"):
        return "https://www.facebook.com" + url
    return url


def parse_cookies_to_map(cookies: str) -> Mapping[str, str]:
    cookies_map = {}
    for ck in cookies.split(";"):
        ck_split = ck.split("=")
        if len(ck_split) == 2:
            key, value = ck_split[0].strip(), ck_split[1].strip()
            cookies_map[key] = value

    return cookies_map


def randStr(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get2FaCode(key2fa: str) -> str:
    try:
        twoFaRequests = requests.get(
            "https://2fa.live/tok/" + key2fa.replace(" ", "")
        ).json()
        return twoFaRequests["token"]
    except:
        return str(random.randint(100000, 999999))


def base36encode(number: int) -> str:
    """Convert from Base10 to Base36."""
    # Taken from https://en.wikipedia.org/wiki/Base36#Python_implementation
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    sign = "-" if number < 0 else ""
    number = abs(number)
    result = ""

    while number > 0:
        number, remainder = divmod(number, 36)
        result = chars[remainder] + result

    return sign + result


def generate_session_id():
    """Generate a random session ID between 1 and 9007199254740991."""
    return random.randint(1, 2**53)


def generate_client_id():
    """Generate a random client ID."""

    def gen(length):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    return gen(8) + "-" + gen(4) + "-" + gen(4) + "-" + gen(4) + "-" + gen(12)


def json_minimal(data: Any) -> str:
    """Get JSON data in minimal form."""
    return json.dumps(data, separators=(",", ":"))
