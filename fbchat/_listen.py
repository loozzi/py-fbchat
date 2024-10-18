import json
import queue
import ssl
from typing import Any
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from ._utils import json_minimal


def mqtt_factory(option: dict) -> mqtt.Client:
    client = mqtt.Client(
        client_id=option["client_id"],
        clean_session=option["clean"],
        protocol=mqtt.MQTTv31,
        transport="websockets",
    )
    client.tls_set(
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_NONE,
        tls_version=ssl.PROTOCOL_TLSv1_2,
    )
    client.username_pw_set(option["username"], password="")
    # client.ws_set_options(**option["ws_options"])
    # client.connect("edge-chat.facebook.com", 443)
    # client.loop_start()
    return client


class Listen:
    def __init__(self, client) -> None:
        self.client = client
        self.host = "wss://edge-chat.facebook.com/chat?region=eag&sid={0}".format(
            self.client.session_id
        )

        self.chat_on = json_minimal(True)
        self.user = {
            "u": self.client.session._user_id,
            "s": self.client.session_id,
            "chat_on": self.chat_on,
            "fg": False,
            "d": self.client.client_id,
            "ct": "websocket",
            "aid": 219994525426954,
            "mqtt_sid": "",
            "cp": 3,
            "ecp": 10,
            "st": "/t_ms",
            "pm": [],
            "dc": "",
            "no_auto_fg": True,
            "gas": None,
            "pack": [],
        }

        self.options = {
            "client_id": "mqttwsclient",
            "username": json_minimal(self.user),
            "clean": True,
            "ws_options": {
                "headers": {
                    "Cookie": self.client.session.get_cookies_as_string(),
                    "Origin": "https://www.facebook.com",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
                    "Referer": "https://www.facebook.com/",
                    "Host": "edge-chat.facebook.com",
                },
            },
            "keepalive": 10,
        }

        self.mqtt = mqtt_factory(self.options)

        self.bodyResults = {
            "body": None,  # Nội dung tin nhắn - content message
            "timestamp": 0,  # Thời gian tin nhắn được gửi - The time the message was sent
            "userId": 0,  # Người gửi tin nhắn - Author sent message
            "messageId": None,  # ID tin nhắn - MessageId
            "replyToId": 0,  # Nơi gửi và nơi nhận lại tin nhắn cần phản hồi - \
            # Where to send and receive the message that needs response
            "type": None,  # user/thread
            "attachments": {  # Tệp đính kèm được gửi - Attachment sent
                "id": 0,  # id attachment
                "url": None,  # url attachment
            },
        }
        self.syncToken = None
        self.lastSeqID = None

    def get_last_seq_id(self):
        self.client.fetch_all_threads()
        self.lastSeqID = self.client.session._sequence_id
        print(f"last_seq_id: {self.lastSeqID}")
        return

    def parse_message(self, message: dict) -> dict:
        """Parse a message into a dictionary."""
        response = self.bodyResults
        response["body"] = message.get("body")
        response["timestamp"] = message["messageMetadata"]["timestamp"]
        response["userId"] = message["messageMetadata"]["actorFbId"]
        response["messageId"] = message["messageMetadata"]["messageId"]
        response["replyToId"] = (
            message["messageMetadata"]["threadKey"].get("otherUserFbId")
            if message["messageMetadata"]["threadKey"].get("otherUserFbId") is not None
            else message["messageMetadata"]["threadKey"].get("threadFbId")
        )
        response["type"] = (
            "user"
            if message["messageMetadata"]["threadKey"].get("otherUserFbId") is not None
            else "thread"
        )
        try:
            if len(message["attachments"]) > 0:
                try:
                    response["attachments"]["id"] = message["attachments"][0]["fbid"]
                    response["attachments"]["url"] = message["attachments"][0][
                        "mercury"
                    ]["blob_attachment"]["preview"]["uri"]
                except Exception as e:
                    response["attachments"]["id"] = "This is image_url!?"
                    print(e)
        except Exception as e:
            response["attachments"]["id"] = None
            response["attachments"]["url"] = None
            print(e)

        return response

    def listen(self, q: queue.Queue) -> None:
        """Listen to incoming Facebook events."""

        def on_connect(client: mqtt.Client, userdata: Any, flags: Any, rc):
            topics = None

            queue = {
                "sync_api_version": 10,
                "max_deltas_able_to_process": 1000,
                "delta_batch_size": 500,
                "encoding": "JSON",
                "entity_fbid": self.client.session._user_id,
            }

            if self.syncToken is None:
                topics = "/messenger_sync_create_queue"
                queue["initial_titan_sequence_id"] = self.lastSeqID
                queue["device_params"] = None
            else:
                topics = "/messenger_sync_get_diffs"
                queue["last_seq_id"] = self.lastSeqID
                queue["sync_token"] = "1"

            client.publish(
                topics,
                json_minimal(queue),
                qos=1,
                retain=False,
            )

        def on_message(client: mqtt.Client, userdata: Any, msg: Any):
            try:
                j = json.loads(msg.payload.decode("utf-8"))
            except Exception as e:
                print(e)
                print(msg.payload)
                return

            if j.get("deltas") is not None:
                dataResponseRaw = j["deltas"][0]
                if dataResponseRaw.get("messageMetadata") is not None:
                    response = self.parse_message(dataResponseRaw)
                    # Pass data to another thread here
                    # open(".mqttMessage", "w", encoding="utf-8").write(
                    #     json.dumps(self.bodyResults, indent=5)
                    # )
                    q.put(response)

            if "syncToken" in j and "firstDeltaSeqId" in j:
                self.syncToken = j["syncToken"]
                self.lastSeqID = j["firstDeltaSeqId"]
                return
            if "lastIssuedSeqId" in j:
                self.lastSeqID = j["lastIssuedSeqId"]
            if "errorCode" in j:
                error = j["errorCode"]
                print(f"ERR {error}")
                # ERROR_QUEUE_NOT_FOUND means that the queue was deleted, since too
                # much time passed, or that it was simply missing
                # ERROR_QUEUE_OVERFLOW means that the sequence id was too small, so
                # the desired events could not be retrieved
                self.syncToken = None
                self.get_last_seq_id()  # update self.lastSeqID
                on_connect()

        def on_disconnect(client: mqtt.Client, userdata: Any, rc: Any):
            print("Disconnected with result code " + str(rc))

        parsed_host = urlparse(self.host)
        self.mqtt.ws_set_options(
            path=f"{parsed_host.path}?{parsed_host.query}",
            headers=self.options["ws_options"]["headers"],
        )

        self.mqtt.on_connect = on_connect
        self.mqtt.on_message = on_message
        self.mqtt.on_disconnect = on_disconnect

        self.mqtt.connect(
            host=self.options["ws_options"]["headers"]["Host"],
            port=443,
            keepalive=self.options["keepalive"],
        )
        self.mqtt.loop_forever()

    def create_queue(self):
        """Create a queue."""
        return queue.Queue()
