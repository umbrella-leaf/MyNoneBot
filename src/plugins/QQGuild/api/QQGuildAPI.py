from nonebot.adapters import Bot
from typing import Optional, Dict, Tuple
from random import randint
import re
import httpx


class QQGuildRoleInfo:
    def __init__(self, role: dict):
        self.id = role['role_id']
        self.name = role['role_name']
        self.max_count = role['max_count']
        self.member_count = role['member_count']

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


class QQGuildCreateRoleInfo:
    def __init__(self, color, name, user):
        self.color = color
        self.name = name
        self.user = user

    def to_dict(self):
        return {
            "color": self.color,
            "name": self.name,
            "initial_users": [str(self.user)]
        }


class QQGuildAPI:
    RecognizeChannelName = '身份🆔认证'
    CheaterReportChannelID = '1473004'
    MaximumRoleNum = 37
    qqno_pattern = re.compile(r'\[CQ:at,qq=(.*?)]')
    image_pattern = re.compile(r'\[CQ:image,file=(.*?),.*?]')
    video_pattern = re.compile(r'\[CQ:video,file=(.*?),.*?]')
    video_urls_pattern = re.compile(r'\[CQ:video.*?url=(.*?)]')
    resource_path = "https://report.umbrella-leaf.com"

    @staticmethod
    async def GetGuildChannelList(guild_id: int, bot: Bot):
        channelInfos = await bot.call_api("get_guild_channel_list",
                                          guild_id=guild_id,
                                          no_cache=False)
        return channelInfos

    @staticmethod
    async def GetCertainChannelId(guild_id: int, bot: Bot, name: str) -> Optional[int]:
        channelInfos = await QQGuildAPI.GetGuildChannelList(guild_id, bot)
        for channelInfo in channelInfos:
            if channelInfo['channel_name'] == name:
                return channelInfo['channel_id']
        return None

    @staticmethod
    async def GetGuildRoles(guild_id: int, bot: Bot):
        guildRoles = await bot.call_api("get_guild_roles", guild_id=guild_id)
        return guildRoles
    
    @staticmethod
    async def DeleteGuildRole(guild_id: int, bot: Bot, role_id: int):
        await bot.call_api("delete_guild_role", guild_id=guild_id, role_id=role_id)

    @staticmethod
    async def BuildGuildIdentities(guild_id: int, bot: Bot) -> Dict[str, QQGuildRoleInfo]:
        """
        获取频道所有身份组
        """
        guildRoles = await QQGuildAPI.GetGuildRoles(guild_id, bot)
        guildIdentitiesByName = {}
        for guildRole in guildRoles:
            guildIdentitiesByName[guildRole['role_name']] = QQGuildRoleInfo(role=guildRole)
        return guildIdentitiesByName

    @staticmethod
    async def CreateGuildRole(guild_id: int, bot: Bot, name: str, user_id: int):
        rgba = RandomArgb()
        create_info = QQGuildCreateRoleInfo(color=rgba.HexToDec(), name=name, user=user_id)
        role_id = await bot.call_api("create_guild_role", guild_id=guild_id, **create_info.to_dict())
        return role_id
    
    @staticmethod
    async def SetGuildMemberRole(guild_id: int, bot: Bot, role_id: int, user_id: int) -> bool:
        stop_roles = [2, 4, 5]
        if role_id in stop_roles:
            return False
        await bot.call_api("set_guild_member_role", guild_id=guild_id, set=True, role_id=role_id, users=[str(user_id)])
        return True
       
    @staticmethod
    async def QuitGuildMemberRole(guild_id: int, bot: Bot, role_id: int, user_id: int) -> bool:
        stop_roles = [2, 4, 5]
        if role_id in stop_roles:
            return False
        await bot.call_api("set_guild_member_role", guild_id=guild_id, set=False, role_id=role_id, users=[str(user_id)])
        return True
    
    @staticmethod
    async def GetGuildMemberProfile(guild_id: int, bot: Bot, user_id: int):
        profile = await bot.call_api("get_guild_member_profile", guild_id=guild_id, user_id=user_id)
        return profile
    
    @staticmethod
    async def MemberInRole(guild_id: int, bot: Bot, user_id: int, role_id: int) -> bool:
        roles = (await QQGuildAPI.GetGuildMemberProfile(guild_id, bot, user_id))['roles']
        for role in roles:
            if int(role['role_id']) == role_id:
                return True
        return False

    @staticmethod
    async def GetMessageInfo(guild_id: int, bot: Bot, message: str) -> Tuple[str, str]:
        # 正则取信息，重新拼接
        at_user_ids = QQGuildAPI.qqno_pattern.findall(message)
        images = QQGuildAPI.image_pattern.findall(message)
        videos = QQGuildAPI.video_pattern.findall(message)
        appendix_urls = images + videos
        video_urls = QQGuildAPI.video_urls_pattern.findall(message)
        list(map(QQGuildAPI.acquireVideoResource, zip(videos, video_urls)))
        message = re.sub(QQGuildAPI.qqno_pattern, "", re.sub(QQGuildAPI.image_pattern, "", re.sub(QQGuildAPI.video_pattern, "", message)))
        for i in range(len(at_user_ids)):
            at_user_ids[i] = "@" + (await QQGuildAPI.GetGuildMemberProfile(guild_id, bot, at_user_ids[i]))['nickname']
        at_user_ids.append(message)
        # 消息拼接
        message = ' '.join(at_user_ids)
        # 附件url拼接
        appendix_urls = ' '.join(list(map(QQGuildAPI.replaceResourceUrl, appendix_urls)))
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
    def acquireVideoResource(video_tuple):
        video_name = video_tuple[0]
        video_url = video_tuple[1]
        video_url = video_url.replace("&amp;", "&")
        client = httpx.Client()
        response = client.get(video_url)
        with open(f"resources/videos/{video_name}", "wb") as fw:
            fw.write(response.content)
        client.close()


def RandomArgb() -> ARGB:
    return ARGB(
        a=randint(50, 255),
        r=randint(50, 255),
        g=randint(50, 255),
        b=randint(50, 255)
    )