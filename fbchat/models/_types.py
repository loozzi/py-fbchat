from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from .._enums import EmojiSize


class MessageType(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass


class Text(MessageType):
    def __init__(self, text: str) -> None:
        self.text = text

    def to_dict(self) -> dict:
        return {
            "body": self.text,
        }


class Emoji(MessageType):
    def __init__(self, emoji: str, size: EmojiSize) -> None:
        self.emoji = emoji
        self.size = size

    def to_dict(self) -> dict:
        return {
            "body": self.emoji,
            "tags[0]": "hot_emoji_size:{}".format(self.size.name.lower()),
        }


class Sticker(MessageType):
    def __init__(self, sticker_id: str) -> None:
        self.sticker_id = sticker_id

    def to_dict(self) -> dict:
        return {
            "sticker_id": self.sticker_id,
        }


class Attachments(MessageType):
    def __init__(self, files: Iterable[Tuple[str, str]]) -> None:
        self.files = files

    def to_dict(self) -> dict:
        data = {}
        data["has_attachment"] = True
        for i, (file_id, mimetype) in enumerate(self.files):
            data["{}s[{}]".format(mimetype, i)] = file_id
        return data


class Location(MessageType):
    def __init__(self, latitude: float, longitude: float, current: bool = True) -> None:
        """
        params:
            latitude: float: Latitude of the location
            longitude: float: Longitude of the location
            current: bool: Whether the location is the current one
        """
        self.latitude = latitude
        self.longitude = longitude
        self.current = current

    def to_dict(self) -> dict:
        data = {}
        data["location_attachment[coordinates][latitude]"] = self.latitude
        data["location_attachment[coordinates][longitude]"] = self.longitude
        data["location_attachment[is_current_location]"] = self.current
        return data
