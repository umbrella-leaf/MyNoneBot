import os.path

from nonebot.adapters.qq import Bot
from nonebot.adapters.qq.event import GuildMessageEvent
from nonebot.adapters.qq.models import (
    Role,
    User,
    Member,
    Channel,
    GetGuildRolesReturn,
    PostGuildRoleReturn
)
from typing import Optional, Dict, Tuple, List
from random import randint
import re
import uuid
import httpx


class QQGuildRoleInfo:
    def __init__(self, role: Role):
        self.id = role.id
        self.name = role.name
        self.max_count = role.member_limit
        self.member_count = role.number

    def IsOverWhelm(self):
        return self.member_count >= self.max_count

    def IsEmpty(self):
        return self.member_count - 1 == 0


class ARGB:
    def __init__(self, a: int, r: int, g: int, b: int):
        self.a = a
        self.r = r
        self.g = g
        self.b = b

    def HexToDec(self):
        return self.b * 256 ** 0 + \
            self.g * 256 ** 1 + \
            self.r * 256 ** 2 + \
            self.a * 256 ** 3


class QQGuildAPI:
    RecognizeChannelName = '身份🆔认证'
    CheaterReportChannelID = '294887937'
    # CheaterReportChannelID = '1473004'
    MaximumRoleNum = 37
    resource_path = "https://report.umbrella-leaf.com"

    @staticmethod
    async def GetGuildChannelList(guild_id: str, bot: Bot):
        channelInfos: List[Channel] = await bot.call_api("get_channels",
                                                         guild_id=guild_id)
        return channelInfos

    @staticmethod
    async def GetCertainChannelId(guild_id: str, bot: Bot, name: str) -> Optional[str]:
        channelInfos = await QQGuildAPI.GetGuildChannelList(guild_id, bot)
        for channelInfo in channelInfos:
            if channelInfo.name == name:
                return channelInfo.id
        return None

    @staticmethod
    async def GetGuildRoles(guild_id: str, bot: Bot):
        guildRoles: GetGuildRolesReturn = await bot.call_api("get_guild_roles", guild_id=guild_id)
        return guildRoles.roles

    @staticmethod
    async def DeleteGuildRole(guild_id: str, bot: Bot, role_id: str):
        await bot.call_api("delete_guild_role", guild_id=guild_id, role_id=role_id)

    @staticmethod
    async def BuildGuildIdentities(guild_id: str, bot: Bot) -> Dict[str, QQGuildRoleInfo]:
        """
        获取频道所有身份组
        """
        guildRoles = await QQGuildAPI.GetGuildRoles(guild_id, bot)
        guildIdentitiesByName = {}
        for guildRole in guildRoles:
            guildIdentitiesByName[guildRole.name] = QQGuildRoleInfo(role=guildRole)
        return guildIdentitiesByName

    @staticmethod
    async def CreateGuildRole(guild_id: str, bot: Bot, name: str, user_id: str):
        rgba = RandomArgb()
        result: PostGuildRoleReturn = await bot.call_api("post_guild_role", guild_id=guild_id, name=name, color=rgba.HexToDec())
        role_id = result.role_id
        await bot.call_api("put_guild_member_role", guild_id=guild_id, role_id=role_id, user_id=user_id)
        return role_id

    @staticmethod
    async def SetGuildMemberRole(guild_id: str, bot: Bot, role_id: str, user_id: str) -> bool:
        stop_roles = ['2', '4', '5']
        if role_id in stop_roles:
            return False
        await bot.call_api("put_guild_member_role", guild_id=guild_id, role_id=role_id, user_id=user_id)
        return True

    @staticmethod
    async def QuitGuildMemberRole(guild_id: str, bot: Bot, role_id: str, user_id: str) -> bool:
        stop_roles = ['2', '4', '5']
        if role_id in stop_roles:
            return False
        await bot.call_api("delete_guild_member_role", guild_id=guild_id, role_id=role_id, user_id=user_id)
        return True

    @staticmethod
    async def GetGuildMemberProfile(guild_id: str, bot: Bot, user_id: str):
        profile: Member = await bot.call_api("get_member", guild_id=guild_id, user_id=user_id)
        return profile

    @staticmethod
    async def MemberInRole(guild_id: str, bot: Bot, user_id: str, role_id: str) -> bool:
        roles = (await QQGuildAPI.GetGuildMemberProfile(guild_id, bot, user_id)).roles
        for role in roles:
            if role == role_id:
                return True
        return False

    @staticmethod
    async def GetMessageInfo(guild_id: str, bot: Bot, message: GuildMessageEvent) -> Tuple[str, str]:
        # 正则取信息，重新拼接
        bot_id = bot.self_info.id
        mentions = [f"@{mention.username}" for mention in message.mentions if mention.id != bot_id] if message.mentions else []
        attachments = [attachment.url for attachment in message.attachments] if message.attachments else []
        appendix_urls = list(map(QQGuildAPI.acquireResources, attachments))
        message = str(message.get_message().get("text"))

        # 消息拼接
        mentions.append(message)
        message = ' '.join(mentions)
        # 附件url拼接
        appendix_urls = ' '.join(appendix_urls)
        return message, appendix_urls

    @staticmethod
    def replaceResourceUrl(path: str) -> str:
        path = path.replace("&amp;", "&")
        if path.endswith("image"):
            path = f"{QQGuildAPI.resource_path}/images/{path}"
        else:
            path = f"{QQGuildAPI.resource_path}/videos/{path}"
        return path

    @staticmethod
    def acquireResources(resource: str):
        resource_name, resource_url = str(uuid.uuid4()), resource.replace("&amp;", "&")
        is_video = (resource_name[-5:] == "video")
        for folder in ["videos", "images"]:
            os.makedirs(f"resources/{folder}", exist_ok=True)

        save_path = f"videos/{resource_name}.mp4" if is_video else f"images/{resource_name}.png"
        with httpx.Client() as client:
            response = client.get(resource_url)
            with open(f"resources/{save_path}", "wb") as fw:
                fw.write(response.content)
        return f"{QQGuildAPI.resource_path}/{save_path}"


def RandomArgb() -> ARGB:
    return ARGB(
        a=randint(50, 255),
        r=randint(50, 255),
        g=randint(50, 255),
        b=randint(50, 255)
    )
