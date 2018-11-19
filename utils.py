import json


def encode_message(message: dict) -> bytes:
    return json.dumps(message).encode("utf-8")


def decode_message(message: bytes) -> dict:
    return json.loads(message.decode("utf-8"))


def get_message_template() -> dict:
    return {
        "nickname": "",
        "action": "",
        "text": ""
    }

