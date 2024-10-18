import json
from typing import List

import requests

from ._auth import Auth
from ._session import Session


class Client:
    def __init__(self) -> None:
        self.session = Session()
        self.auth = Auth(self.session)

    def get_session(self) -> requests.Session:
        return self.session.__session__

    def fetch_users(self) -> List:
        payload = {
            "viewer": self.session._user_id,
        }

        response = self.session._post(
            "https://www.facebook.com/chat/user_info_all", data=payload, as_graphql=0
        )

        users = []
        if "for (;;);" in response.text:
            response = response.text.replace("for (;;);", "")
            response_json = json.loads(response)
            for user in response_json["payload"].values():
                if user["type"] not in ["user", "friend"] or user["id"] in ["0", 0]:
                    continue
                users.append(user)

        return users

    def fetch_all_threads(self, limit: int = 1):
        query = json.dumps(
            {
                "o0": {
                    "doc_id": "3336396659757871",
                    "query_params": {
                        "limit": limit,
                        "before": None,
                        "tags": ["INBOX"],
                        "includeDeliveryReceipts": False,
                        "includeSeqID": True,
                    },
                }
            }
        )

        response = self.session._post(
            "https://www.facebook.com/api/graphqlbatch/",
            data={"queries": query},
            as_graphql=True,
        )
        response_text = response.text.split('{"successful_results"')[0]
        response_json = json.loads(response_text)
        return response_json["o0"]["data"]["viewer"]["message_threads"]["nodes"]

    def fetch_threads(self):
        threads = self.fetch_all_threads()
        thread_ids = []
        thread_names = []
        for thread in threads:
            thread_id = thread["thread_key"]["thread_fbid"]
            thread_name = thread.get("name")
            if thread_id is not None:
                thread_ids.append(thread_id)
                thread_names.append(thread_name)

        return {"thread_ids": thread_ids, "thread_names": thread_names}
