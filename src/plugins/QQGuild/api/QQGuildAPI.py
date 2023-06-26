from nonebot.adapters import Bot
from typing import Optional, Dict
from random import randint


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
    MaximumRoleNum = 37

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
        roles = (await bot.call_api("get_guild_member_profile", guild_id=guild_id, user_id=user_id))['roles']
        return roles
    
    @staticmethod
    async def MemberInRole(guild_id: int, bot: Bot, user_id: int, role_id: int) -> bool:
        roles = await QQGuildAPI.GetGuildMemberProfile(guild_id, bot, user_id)
        for role in roles:
            if int(role['role_id']) == role_id:
                return True
        return False


def RandomArgb() -> ARGB:
    return ARGB(
        a=randint(50, 255),
        r=randint(50, 255),
        g=randint(50, 255),
        b=randint(50, 255)
    )