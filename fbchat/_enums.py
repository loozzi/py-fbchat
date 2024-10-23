import enum


class ReactionType(enum.Enum):
    ADD = "ADD_REACTION"
    REMOVE = "REMOVE_REACTION"


class EmojiSize(enum.Enum):
    LARGE = "369239383222810"
    MEDIUM = "369239343222814"
    SMALL = "369239263222822"


class AttachmentType(enum.Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    VIDEO_MP4 = "video/mp4"
    AUDIO_OGG = "audio/ogg"
    AUDIO_MPEG = "audio/mpeg"
    FILE = "file"
