from typing import Mapping

from ._login import Login
from ._user import User
from ._utils import session_factory


class Session:
    def __init__(self):
        self.__session__ = session_factory()
        self.login = Login(self.__session__)
        self.user = User(self.__session__)

        self.data_home_page = None

    def get_cookies(self) -> Mapping[str, str]:
        """Retrieve session cookies, that can later be used in `from_cookies`.

        Returns:
            A dictionary containing session cookies

        Example:
            >>> cookies = session.get_cookies()
        """
        return self.__session__.cookies.get_dict()

    def is_logged_in(self):
        return self.login.is_logged_in()
