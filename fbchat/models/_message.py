import json
from typing import Any, Iterable, Tuple

import requests

from .._enums import ReactionType


class Message:
    def __init__(self, client) -> None:
        self.client = client

    def __get_params__(self) -> dict:
        pass

    def send_text(
        self,
        text: str = None,
        thread_id: str = None,
        mentions: Any = None,
        files: Iterable[Tuple[str, str]] = None,
        reply_to_id: str = None,
        type: str = "user",
    ) -> requests.Response:
        data = {}
        data["action_type"] = "ma-type:user-generated-message"
        if text is not None:
            data["body"] = text

        # TODO: Implement mentions here

        if type == "user":
            if isinstance(thread_id, list):
                for i, thread_id in enumerate(thread_id):
                    data["specific_to_list[" + str(i) + "]"] = "fbid:" + thread_id
                data["specific_to_list[" + str(len(thread_id)) + "]"] = (
                    "fbid:" + self.client.session._user_id
                )
            else:
                data["specific_to_list[0]"] = "fbid:" + thread_id
                data["specific_to_list[1]"] = "fbid:" + self.client.session._user_id
                data["other_user_fbid"] = thread_id
        else:
            data["thread_fbid"] = thread_id

        if files:
            data["has_attachment"] = True

        for i, (file_id, mimetype) in enumerate(files or ()):
            data["{}s[{}]".format(mimetype, i)] = file_id

        if reply_to_id:
            data["replied_to_message_id"] = reply_to_id

        return self.client.session._do_send_request(data)

    def send_emoji(self, emoji: str, size: Any) -> requests.Response:
        pass

    def send_sticker(self, sticker_id: str) -> requests.Response:
        pass

    def send_files(self, files: Any, message: str) -> requests.Response:
        return self.send_text(text=message, files=files)

    def reply_reaction(
        self, message_id: str, reaction: str, action: ReactionType = ReactionType.ADD
    ) -> requests.Response:
        data = {}
        data["variables"] = json.dumps(
            {
                "data": {
                    "action": action.value,
                    "client_mutation_id": "1",
                    "actor_id": self.client.session._user_id,
                    "message_id": message_id,
                    "reaction": reaction,
                }
            }
        )
        # random.choice(["🥺","😏", "✅","😎","😭", "🫥", "✈️", "✅", "🌚", "😵", "😮‍💨", "😷", "🥹", "😒", "🐧",
        # "💩", "🍦", "👀", "💀", "🐣", "💔", "🫶🏻", "🪐", "🙈", "🐈‍⬛", "🦆", "🔪", "⚙️", "🧭", "📡", "💌", "⁉️", "💀"])
        data["dpr"] = 1
        data["doc_id"] = "1491398900900362"

        return self.client.session._post(
            "https://www.facebook.com/webgraphql/mutation/",
            data=data,
            as_graphql=0,
        )
