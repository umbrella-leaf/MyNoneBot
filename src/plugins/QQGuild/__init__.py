from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    MessageEvent as QQMessageEvent,
    MessageSegment as QQMessageSegment
)
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot_plugin_guild_patch import GuildMessageEvent
from typing import Union
from .api import *

recognize = on_command("申请认证", priority=11, block=True)
quit = on_command("取消认证", priority=12, block=True)

Bot = QQBot
Event = Union[QQMessageEvent, GuildMessageEvent]


@recognize.handle()
async def handle_recognize(bot: Bot, event: Event, args: Message = CommandArg()):
    if not isinstance(event, GuildMessageEvent):
        await recognize.finish()
    else:
        guild_id = event.guild_id
        channel_id = event.channel_id
        user_id = event.user_id
        recognize_channel_id = await QQGuildAPI.GetCertainChannelId(guild_id, bot, name=QQGuildAPI.RecognizeChannelName)
        if str(channel_id) != recognize_channel_id:
            tip = "请到身份认证频道进行认证！"
        else:
            identity = args.extract_plain_text().strip()
            identities = await QQGuildAPI.BuildGuildIdentities(guild_id, bot)
            # 在现有身份组中
            if identity in identities:
                target_identity = identities[identity]
                # 身份组满员
                if target_identity.IsOverWhelm():
                    tip = "不好意思，该身份组已经满员啦！"
                else:
                    if not await QQGuildAPI.SetGuildMemberRole(guild_id, bot, int(target_identity.id), user_id):
                        tip = "该身份组不可加入！"
                    else:
                        tip = f"您成功加入身份组<{identity}>"
            # 不在现有身份组中
            else:
                if len(identities) < QQGuildAPI.MaximumRoleNum:
                    await QQGuildAPI.CreateGuildRole(guild_id, bot, identity, user_id)
                    available = QQGuildAPI.MaximumRoleNum - len(identities) - 1
                    tip = f"您成功加入身份组<{identity}>，还可新增{available}个身份组"
                else:
                    tip = "身份组已满，不可新增!"
        await recognize.finish(QQReplyMessage(tip, event))


@quit.handle()
async def handle_quit(bot: Bot, event: Event, args: Message = CommandArg()):
    if not isinstance(event, GuildMessageEvent):
        await quit.finish()
    else:
        guild_id = event.guild_id
        channel_id = event.channel_id
        user_id = event.user_id
        recognize_channel_id = await QQGuildAPI.GetCertainChannelId(guild_id, bot, name=QQGuildAPI.RecognizeChannelName)
        if str(channel_id) != recognize_channel_id:
            await quit.finish(QQReplyMessage("请到身份认证频道取消认证！", event))
        else:
            identity = args.extract_plain_text().strip()
            identities = await QQGuildAPI.BuildGuildIdentities(guild_id, bot)
            # 在现有身份组中
            if identity in identities:
                target_identity = identities[identity]
                role_id = int(target_identity.id)
                if not await QQGuildAPI.MemberInRole(guild_id, bot, user_id, role_id):
                    await quit.finish(QQReplyMessage("您不在该身份组中！", event))
                else:
                    if not await QQGuildAPI.QuitGuildMemberRole(guild_id, bot, role_id, user_id):
                        await quit.finish(QQReplyMessage("该身份组不可退出哦", event))
                    tip = f"您成功退出身份组<{identity}>"
                    if target_identity.IsEmpty():
                        await QQGuildAPI.DeleteGuildRole(guild_id, bot, role_id)
                        available = QQGuildAPI.MaximumRoleNum - len(identities) + 1
                        tip += f"，还可新增{available}个身份组"
                    await quit.finish(QQReplyMessage(tip, event))
            # 不在现有身份组中
            else:
                await quit.finish(QQReplyMessage("该身份组不存在！", event))


def QQReplyMessage(message: Union[str, QQMessageSegment], event: Event):
    if isinstance(event, GuildMessageEvent):
        return QQMessageSegment.at(user_id=event.user_id) + message
    else:
        return QQMessageSegment.reply(id_=event.message_id) + message
