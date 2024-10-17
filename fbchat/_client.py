import requests

from ._auth import Auth
from ._session import Session
from ._user import User


class Client:
    def __init__(self) -> None:
        self.session = Session()
        self.user = User(self.session)
        self.auth = Auth(self.session)

    def get_session(self) -> requests.Session:
        return self.session.__session__
