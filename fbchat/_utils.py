import random
import string
from typing import Mapping

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