import enum
import sys
from typing import Optional

import attr


class ThreadLocation(enum.Enum):
    """Used to specify where a thread is located (inbox, pending, archived, other)."""

    INBOX = "INBOX"
    PENDING = "PENDING"
    ARCHIVED = "ARCHIVED"
    OTHER = "OTHER"

    @classmethod
    def _parse(cls, value: str):
        return cls(value.lstrip("FOLDER_"))


@attr.s(frozen=True, slots=True, kw_only=sys.version_info[:2] > (3, 5))
class Image:
    #: URL to the image
    url = attr.ib(type=str)
    #: Width of the image
    width = attr.ib(None, type=Optional[int])
    #: Height of the image
    height = attr.ib(None, type=Optional[int])

    @classmethod
    def _from_uri(cls, data):
        return cls(
            url=data["uri"],
            width=int(data["width"]) if data.get("width") else None,
            height=int(data["height"]) if data.get("height") else None,
        )

    @classmethod
    def _from_url(cls, data):
        return cls(
            url=data["url"],
            width=int(data["width"]) if data.get("width") else None,
            height=int(data["height"]) if data.get("height") else None,
        )

    @classmethod
    def _from_uri_or_none(cls, data):
        if data is None:
            return None
        if data.get("uri") is None:
            return None
        return cls._from_uri(data)

    @classmethod
    def _from_url_or_none(cls, data):
        if data is None:
            return None
        if data.get("url") is None:
            return None
        return cls._from_url(data)
