from nonebot import on_regex, on_command
from random import randint
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    MessageEvent as QQMessageEvent,
    MessageSegment as QQMessageSegment
)
from nonebot.adapters import Message
from nonebot.params import CommandArg
from .data_source import *
from typing import Union

ai_chat = on_regex(pattern=".*?", priority=50, block=False, rule=to_me())
chat_reset = on_command("reset", priority=10, aliases={"重置", "重置对话", }, block=True, rule=to_me())

Bot = Union[QQBot]
Event = Union[QQMessageEvent]


@ai_chat.handle()
async def ai_chat_handler(bot: Bot, event: Event, state: T_State):
    prompt = str(event.get_message()).strip()
    bot_nickname = str(dict(event.dict()).get("raw_message"))[0:2]
    reply = None
    if bot_nickname == plugin_config.tencent_bot_nickname:
        reply = await txBot.chat(event, prompt)
    elif bot_nickname == plugin_config.newbing_bot_nickname:
        reply = await bingBot.chat(event, prompt)
    elif bot_nickname == plugin_config.ernie_bot_nickname:
        reply = await ernieBot.chat(event, prompt)
    else:
        reply = await doubaoBot.chat(event, prompt)
    if reply:
        await ai_chat.finish(QQReplyMessage(reply, event))
    else:
        fallback = plugin_config.expr_dont_understand[randint(0, 3)]
        await ai_chat.finish(QQReplyMessage(fallback, event))


@chat_reset.handle()
async def chat_reset_handler(bot: Bot, event: Event,
                             state: T_State, args: Message = CommandArg()):
    bot_nickname = str(dict(event.dict()).get("raw_message"))[0:2]
    if bot_nickname == plugin_config.newbing_bot_nickname:
        await bingBot.reset_chat(bingBot.get_convo_id_from_session(event=event), force=True)
    elif bot_nickname == plugin_config.ernie_bot_nickname:
        await ernieBot.reset_chat(ernieBot.get_convo_id_from_session(event=event), force=True)
    elif bot_nickname == plugin_config.tencent_bot_nickname:
        await txBot.reset_chat(txBot.get_convo_id_from_session(event=event), force=True)
    else:
        await doubaoBot.reset_chat(doubaoBot.get_convo_id_from_session(event=event), force=True)
    await chat_reset.finish(message=QQReplyMessage("您的对话已重置", event))


def QQReplyMessage(message: Union[str, QQMessageSegment], event: Event):
    return QQMessageSegment.reply(id_=event.message_id) + message
