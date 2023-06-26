import json
from typing import Optional
from nonebot.adapters.onebot.v11 import Event, MessageEvent, GroupMessageEvent
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tbp.v20190627 import tbp_client, models
from .base_bot import Bot


class TencentBot(Bot):
    def __init__(self, secret_id: str,
                 secret_key: str,
                 bot_id: str,
                 redis_cli,
                 key_prefix: str,
                 session_expire: int):
        # 初始化客户端
        cred = credential.Credential(
            secret_id=secret_id,
            secret_key=secret_key
        )
        httpProfile = HttpProfile()
        httpProfile.endpoint = 'tbp.tencentcloudapi.com'
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.__chatbot = tbp_client.TbpClient(cred, "", clientProfile)
        self.bot_id = bot_id
        self.redis = redis_cli
        self.key_prefix = key_prefix
        self.session_expire = session_expire

    def get_convo_id_from_session(self, event: Event) -> str:
        user_id = "user"
        if isinstance(event, MessageEvent) or isinstance(event, GroupMessageEvent):
            user_id = event.user_id
            user_id = str(user_id)
        group_id = "personal"
        if isinstance(event, GroupMessageEvent):
            group_id = event.group_id
            group_id = str(group_id)
        return f"{self.key_prefix}-{group_id}-{user_id}"
    
    def get_convo_id_from_wx_oa(self, user_id: str):
        return f"{self.key_prefix}_wx_oa_{user_id}"

    async def reset_chat(self, convo_id: str, force: bool):
        if force or self.redis.get(convo_id) is None:
            await self.reset(convo_id=convo_id)
        # 提问前，即使对话过期，也不重设过期时间，而是等到回答结束才重设，但如果强制重置则立即重设过期时间
        if force:
            await self.reset_expire(convo_id=convo_id)

    async def reset_expire(self, convo_id: str):
        self.redis.set(convo_id, "1", ex=self.session_expire)

    async def wx_oa_reset_chat(self, user_id: str, force: bool):
        convo_id = self.get_convo_id_from_wx_oa(user_id=user_id)
        if force or self.redis.get(convo_id) is None:
            await self.wx_oa_reset(user_id=user_id)
        self.redis.set(convo_id, "1", ex=self.session_expire)

    async def reset(self, convo_id: str):
        try:
            params = {
                "BotId": self.bot_id,
                "BotEnv": "dev",
                "TerminalId": convo_id,
                "PlatformType": "MiniProgram"
            }
            req = models.TextResetRequest()
            req.from_json_string(json.dumps(params))

            chatbot = self.get_chat_bot()
            resp = chatbot.TextReset(req)
        except TencentCloudSDKException as err:
            print(err)

    async def wx_oa_reset(self, user_id: str):
        try:
            params = {
                "BotId": self.bot_id,
                "BotEnv": "dev",
                "TerminalId": self.get_convo_id_from_wx_oa(user_id=user_id),
                "PlatformType": "MiniProgram"
            }
            req = models.TextResetRequest()
            req.from_json_string(json.dumps(params))

            chatbot = self.get_chat_bot()
            resp = chatbot.TextReset(req)
        except TencentCloudSDKException as err:
            print(err)

    async def chat(self, event: Event, prompt: Optional[str]) -> Optional[str]:
        convo_id = self.get_convo_id_from_session(event=event)
        if not prompt:
            return None
        try:
            params = {
                "BotId": self.bot_id,
                "BotEnv": "dev",
                "TerminalId": convo_id,
                "InputText": prompt,
                "PlatformType": "MiniProgram"
            }
            req = models.TextProcessRequest()
            req.from_json_string(json.dumps(params))

            chatbot = self.get_chat_bot()
            await self.reset_chat(convo_id=convo_id, force=False)
            resp = chatbot.TextProcess(req).ResponseMessage
            reply = resp.GroupList[0].Content
            await self.reset_expire(convo_id=convo_id)
            return reply
        except TencentCloudSDKException as err:
            print(err)
            return None
        
    async def wx_oa_chat(self, user_id: str, prompt: Optional[str]) -> Optional[str]:
        if not prompt:
            return None
        try:
            params = {
                "BotId": self.bot_id,
                "BotEnv": "dev",
                "TerminalId": self.get_convo_id_from_wx_oa(user_id=user_id),
                "InputText": prompt,
                "PlatformType": "MiniProgram"
            }
            req = models.TextProcessRequest()
            req.from_json_string(json.dumps(params))

            chatbot = self.get_chat_bot()
            await self.wx_oa_reset_chat(user_id=user_id, force=False)
            resp = chatbot.TextProcess(req).ResponseMessage
            reply = resp.GroupList[0].Content
            return reply
        except TencentCloudSDKException as err:
            print(err)
            return None

    def get_chat_bot(self):
        return self.__chatbot

