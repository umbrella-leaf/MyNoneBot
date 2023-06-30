from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    MessageEvent as QQMessageEvent,
    MessageSegment as QQMessageSegment
)
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot_plugin_guild_patch import GuildMessageEvent
from .data_source import translator
from typing import Union


translate = on_command("翻译", priority=30, aliases={"translate", }, block=True, rule=to_me())

Bot = QQBot
Event = Union[QQMessageEvent, GuildMessageEvent]


@translate.handle()
async def translate_handler(bot: Bot, event: Event, state: T_State, args: Message = CommandArg()):
    source_text = args.extract_plain_text().strip()
    if source_text != "":
        target_text = await translator.translate(text=source_text)
        if target_text:
            await translate.finish(QQReplyMessage(message=f"{source_text}的意思是：{target_text}", event=event))
        await translate.finish(QQReplyMessage(message="翻译出错！", event=event))
    await translate.finish(QQReplyMessage(message="请输入翻译文本！", event=event))


def QQReplyMessage(message: Union[str, QQMessageSegment], event: Event):
    if isinstance(event, GuildMessageEvent):
        return QQMessageSegment.at(user_id=event.user_id) + message
    else:
        return QQMessageSegment.reply(id_=event.message_id) + message
