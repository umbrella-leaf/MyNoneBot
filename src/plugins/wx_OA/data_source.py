from nonebot import require
from .msg import reply, receive
from typing import Optional
from enum import IntEnum

require("ai_chat")
require("jhapi")

from src.plugins.ai_chat import chatBot, txBot, plugin_config as chat_config
from src.plugins.jhapi import jhapi


def get_params(params: dict, name: str):
    if name in params:
        return params.get(name)[0]
    return None


def is_txBot(bot_name: Optional[str]):
    return bot_name == chat_config.tencent_bot_nickname


def is_chatBot(bot_name: Optional[str]):
    return bot_name == chat_config.chatgpt_bot_nickname


class Session(IntEnum):
    Start = 0
    Processing = 1
    End = 2


response_dict = {}