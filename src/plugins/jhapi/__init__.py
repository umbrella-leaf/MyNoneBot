from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    MessageEvent as QQMessageEvent,
    MessageSegment as QQMessageSegment
)
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg, ArgPlainText
from nonebot_plugin_guild_patch import GuildMessageEvent
from .data_source import jhapi
from typing import Union

ai_draw = on_command("ai_draw", priority=14, aliases={"画图", }, block=True, rule=to_me())
fortune = on_command("fortune", priority=15, aliases={"星座运势", "运势图", }, block=True, rule=to_me())
news = on_command("news", priority=16, aliases={"新闻", }, block=True, rule=to_me())
background = on_command("background", priority=17, aliases={"背景图", }, block=True, rule=to_me())


Bot = QQBot
Event = Union[QQMessageEvent, GuildMessageEvent]


@ai_draw.handle()
async def ai_draw_handler(bot: Bot, event: Event,
                          state: T_State, args: Message = CommandArg()):
    desc = args.extract_plain_text().strip()
    if desc != "":
        tip = "正在为您作画，请耐心等待"
        await ai_draw.send(message=QQReplyMessage(tip, event))
        image_url = await jhapi.draw(desc=desc, event=event)
        if image_url.startswith("base64"):
            await ai_draw.finish(message=QQReplyMessage(QQMessageSegment.image(file=image_url), event))
        await ai_draw.finish(message=QQReplyMessage(image_url, event=event))
    else:
        reply = "要描述作画内容哦！"
        await ai_draw.finish(message=QQReplyMessage(reply, event))


@fortune.handle()
async def fortune_handler(bot: Bot, event: Event,
                          state: T_State, args: Message = CommandArg()):
    constellation = args.extract_plain_text().strip()
    if constellation != "":
        image_url = await jhapi.fortune(constellation=constellation)
        if not image_url:
            await fortune.finish(QQReplyMessage("请输入正确的星座名！", event))
        await fortune.finish(message=QQReplyMessage(QQMessageSegment.image(image_url), event))
    else:
        tip = "星座不能为空"
        await ai_draw.finish(message=QQReplyMessage(tip, event))


@news.handle()
async def news_handler(bot: Bot, event: Event,
                       state: T_State):
    image_url = await jhapi.news()
    await news.finish(message=QQReplyMessage(QQMessageSegment.image(image_url), event))


def QQReplyMessage(message: Union[str, QQMessageSegment], event: Event):
    if isinstance(event, GuildMessageEvent):
        return QQMessageSegment.at(user_id=event.user_id) + message
    else:
        return QQMessageSegment.reply(id_=event.message_id) + message
    

@background.handle()
async def background_handler(bot: Bot, event: Event, state: T_State, args: Message = CommandArg()):
    typ = args.extract_plain_text().strip()
    if typ != "":
        image_url, typ_list = await jhapi.background(typ)
        if not image_url:
            await background.send(QQReplyMessage(f"请从以下类型中选择!：{'、'.join(typ_list)}", event))
        else:
            await background.finish(QQReplyMessage(QQMessageSegment.image(image_url), event))
    else:
        _, typ_list = await jhapi.background(typ)
        await background.send(QQReplyMessage(f"请从以下类型中选择!：{'、'.join(typ_list)}", event))


@background.got("typ_msg")
async def choose_bg_type(event: Event, state: T_State, typ_msg: Message = Arg(), typ: str = ArgPlainText("typ_msg")):
    image_url, typ_list = await jhapi.background(typ)
    if not image_url:
        await background.reject(QQReplyMessage(f"请从以下类型中选择!：{'、'.join(typ_list)}", event))
    else:
        await background.finish(QQReplyMessage(QQMessageSegment.image(image_url), event))