import random
from typing import Mapping

from ._utils import session_factory


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

    def is_logged_in(self) -> bool:
        response = self.__session__.get(
            "https://www.facebook.com/login/", allow_redirects=True
        )
        self.__get_requied_data__()
        return response.url == "https://www.facebook.com/home.php"

    def __get_requied_data__(self) -> None:
        __headers__ = {
            "authority": "m.facebook.com",
            "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
                Chrome/100.0.4896.127 Safari/537.36",
        }
        response = self.__session__.get(
            "https://m.facebook.com",
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
