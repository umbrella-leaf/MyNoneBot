from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    MessageEvent as QQMessageEvent,
    MessageSegment as QQMessageSegment
)
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.params import CommandArg, Arg, ArgPlainText
from typing import Union
from .data_source import *

music = on_command("music", aliases={"点歌", }, rule=to_me(), priority=8, block=True)

Bot = QQBot
Event = Union[QQMessageEvent, GuildMessageEvent]


@music.handle()
async def music_handler(bot: Bot, event: Event,
                        state: T_State, args: Message = CommandArg()):
    song_name = args.extract_plain_text().strip()
    if song_name != "":
        if isinstance(event, GuildMessageEvent):
            await music.finish(message=QQReplyMessage("频道内不支持点歌哦！", event))
        elif isinstance(event, QQMessageEvent):
            netease, pooled_object = await borrowNeteaseObject()
            await netease.get_song_infos(song_name)
            song_list = netease.get_song_list()
            if len(netease.songs):
                state["netease"] = netease
                state["pooled_object"] = pooled_object
                await music.send(message=QQReplyMessage(song_list, event))
            else:
                reply = "不好意思，未能找到相关歌曲！"
                await music.finish(message=QQReplyMessage(reply, event))
    else:
        reply = "要说清楚歌名哦"
        await music.finish(message=QQReplyMessage(reply, event))


@music.got("seq")
async def choose_music(event: Event, state: T_State, seq: Message = Arg(), seq_no: str = ArgPlainText("seq")):
    at_me = dict(event.dict()).get("to_me")
    if not at_me:
        await music.reject()
    pooled_object: PooledObject = state.get("pooled_object")
    if seq_no == "取消":
        await recycleNeteaseObject(pooled_object)
        await music.finish(QQReplyMessage("已取消本次点歌", event))
    netease: NeteaseMusic = state.get("netease")
    if not seq_no.isdigit() or int(seq_no) > len(netease.songs) or int(seq_no) <= 0:
        await music.reject(prompt=QQReplyMessage("请输入正确的序号", event))
    else:
        song_url = netease.songs[int(seq_no) - 1].url
        song_name = netease.songs[int(seq_no) - 1].name
        song_info = str(netease.songs[int(seq_no) - 1])
        if song_url:
            await recycleNeteaseObject(pooled_object)
            await music.send(message=QQReplyMessage(f"下面为您带来 {song_info}", event))
            await music.finish(message=QQMessageSegment.record(file=song_url))
            # await music.finish(message=QQMessageSegment.share(url=song_url, title=song_name))
        else:
            await music.reject(prompt=QQReplyMessage("不好意思哦，暂时没有这首歌的版权，请另选择一首", event))


def QQReplyMessage(message: Union[str, QQMessageSegment], event: Event):
    if isinstance(event, GuildMessageEvent):
        return QQMessageSegment.at(user_id=event.user_id) + message
    else:
        return QQMessageSegment.reply(id_=event.message_id) + message
