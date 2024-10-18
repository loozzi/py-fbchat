import json
import queue
import threading
from typing import List

import requests

from ._auth import Auth
from ._listen import Listen
from ._session import Session
from ._utils import generate_client_id, generate_session_id


class Client:
    def __init__(self) -> None:
        self.session = Session()
        self.auth = Auth(self.session)
        self.client_id = generate_client_id()
        self.session_id = generate_session_id()

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
        self.session._sequence_id = response_json["o0"]["data"]["viewer"][
            "message_threads"
        ]["sync_sequence_id"]
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

    def listen(self) -> queue.Queue:
        """
        Listen to messages from the client's Facebook account.
        Returns a queue.Queue object that contains the messages.
        """
        main_event = Listen(self)
        main_event.get_last_seq_id()
        q = main_event.create_queue()
        threading.Thread(target=main_event.listen, args=(q,)).start()

        return q
