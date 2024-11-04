import json
import random
from typing import Any, Mapping, Tuple

import requests

from ._utils import (
    base36encode,
    datetime_to_millis,
    generate_message_id,
    generate_offline_threading_id,
    now,
    session_factory,
)


def client_id_factory() -> str:
    return hex(int(random.random() * 2**31))[2:]


class Session:
    def __init__(self):
        self.__session__ = session_factory()

        # Somes arguments for data form
        self._fb_dtsg = None
        self._user_id = None
        self._revision = None
        self._jazoest = None
        self._fb_dtsg_ag = None
        self._hash = None
        self._session_id = None
        self._counter = 0
        self._client_id = client_id_factory()

    def get_cookies(self) -> Mapping[str, str]:
        """Retrieve session cookies, that can later be used in `from_cookies`.

        Returns:
            A dictionary containing session cookies

        Example:
            >>> cookies = session.get_cookies()
        """
        return self.__session__.cookies.get_dict()

    def get_cookies_as_string(self) -> str:
        """Retrieve session cookies as a string.

        Returns:
            A string containing session cookies

        Example:
            >>> cookies = session.get_cookies_as_string()
        """
        return "; ".join(
            f"{key}={value}" for key, value in self.__session__.cookies.items()
        )

    def get_params(
        self,
        doc_id: Any = None,
        fb_api_req_friendly_name: Any = None,
        require_graphql: Any = None,
    ) -> Mapping[str, str]:
        response = {
            "__a": 1,
            "__user": self._user_id,
            "__rev": self._revision,
            "__req": base36encode(self._counter),
            "av": self._user_id,
            "fb_dtsg": self._fb_dtsg,
        }

        if require_graphql is None:
            response.update(
                {
                    "fb_dtsg_ag": self._fb_dtsg_ag,
                    "jazoest": self._jazoest,
                    "fb_api_caller_class": "RelayModern",
                    "fb_api_req_friendly_name": fb_api_req_friendly_name,
                    "server_timestamps": "true",
                    "doc_id": str(doc_id),
                }
            )

        return response

    def is_logged_in(self) -> bool:
        response = self.__session__.get(
            "https://www.facebook.com/login/", allow_redirects=True
        )
        self.__get_requied_data__()
        return response.url == "https://www.facebook.com/home.php"

    def __get_requied_data__(self) -> None:
        __headers__ = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/130.0.0.0 Safari/537.36",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        response = self.__session__.get(
            "https://www.facebook.com/me",
            headers=__headers__,
            timeout=60000,
            verify=True,
        )

        splitDataList = [
            ["fb_dtsg", '["DTSGInitData",[],{"token":"', '"'],
            ["fb_dtsg_ag", 'async_get_token":"', '"'],
            ["jazoest", "jazoest=", '"'],
            ["hash", 'hash":"', '"'],
            ["sessionID", 'sessionId":"', '"'],
            ["FacebookID", '"actorID":"', '"'],
            ["clientRevision", 'client_revision":', ","],
        ]

        response_text = response.text

        def parseData(data: str, start: str, end: str) -> str:
            try:
                return data.split(start)[1].split(end)[0]
            except:
                return (
                    "Unable to retrieve data for %s. It's possible that they have been deleted or modified."
                    % start
                )

        self._fb_dtsg = parseData(
            response_text, splitDataList[0][1], splitDataList[0][2]
        )
        self._user_id = parseData(
            response_text, splitDataList[5][1], splitDataList[5][2]
        )
        self._revision = parseData(
            response_text, splitDataList[6][1], splitDataList[6][2]
        )
        self._jazoest = parseData(
            response_text, splitDataList[2][1], splitDataList[2][2]
        )
        self._fb_dtsg_ag = parseData(
            response_text, splitDataList[1][1], splitDataList[1][2]
        )
        self._hash = parseData(response_text, splitDataList[3][1], splitDataList[3][2])
        self._counter += 1

    def __set_cookies__(self, cookies: Mapping[str, str]) -> None:
        self.__session__.cookies.update(cookies)

    def _post(self, url, data, files=None, as_graphql=None) -> dict | requests.Response:
        data.update(self.get_params(require_graphql=as_graphql))
        try:
            r = self.__session__.post(url, data=data, files=files)
            r.encoding = "utf-8"
            if r.text is None or len(r.text) == 0:
                raise Exception("Error when sending request: Got empty response")
            if "for (;;);" in r.text:
                response_json = json.loads(r.text.replace("for (;;);", ""))
                if "error" in r:
                    raise Exception("Error: {}".format(r["error"]))
                return response_json
            return r
        except requests.RequestException as e:
            raise Exception(e)

    def _do_send_request(self, data) -> Tuple[str, str]:
        time_now = now()

        offline_threading_id = generate_offline_threading_id()
        data["client"] = "mercury"
        data["author"] = "fbid:{}".format(self._user_id)
        data["timestamp"] = datetime_to_millis(time_now)
        data["timestamp_absolute"] = "Today"
        data["source"] = "source:chat:web"
        data["source_tags[0]"] = "source:chat"
        data["client_thread_id"] = "root:{}".format(self._client_id)
        data["offline_threading_id"] = offline_threading_id
        data["message_id"] = offline_threading_id
        data["threading_id"] = generate_message_id(time_now, self._client_id)
        data["ephemeral_ttl_mode:"] = "0"
        data["manual_retry_cnt"] = "0"
        data["ui_push_phase"] = "V3"

        response = self._post(
            "https://www.facebook.com/messaging/send/", data, as_graphql=False
        )
        if isinstance(response, dict):
            message_ids = [
                (action["message_id"], action["thread_fbid"])
                for action in response["payload"]["actions"]
                if "message_id" in action
            ]
            if len(message_ids) != 1:
                print("Got multiple message ids' back: {}".format(message_ids))
            return message_ids[0]
        else:
            print("No message IDs could be found", data=response)
            return None

    def _post_payload(self, url: str, data: dict, files: None):
        res = self._post(url, data, files)

        try:
            return res["payload"]
        except KeyError:
            raise Exception("No payload in response")
