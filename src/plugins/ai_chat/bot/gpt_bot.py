from typing import Optional
from revChatGPT.V3 import Chatbot
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MessageEvent
from .base_bot import *
import traceback


class ChatGPTBot(Bot):
    def __init__(self, api_key: str,
                 model: str,
                 redis_cli,
                 key_prefix: str,
                 session_expire: int,
                 proxy: str):
        self.__chatbot = Chatbot(
            api_key=api_key,
            engine=model,
            proxy=proxy
        )
        self.redis = redis_cli
        self.key_prefix = key_prefix
        self.session_expire = session_expire

    async def reset_chat(self, convo_id: str, force: bool):
        if force or self.redis.get(convo_id) is None:
            chatbot = self.get_chat_bot()
            chatbot.reset(convo_id=convo_id)
        # 提问前，即使对话过期，也不重设过期时间，而是等到回答结束才重设，但如果强制重置则立即重设过期时间
        if force:
            await self.reset_expire(convo_id)

    async def reset_expire(self, convo_id: str):
        self.redis.set(convo_id, "1", ex=self.session_expire)

    async def wx_oa_reset_chat(self, user_id: str, force: bool):
        convo_id = self.get_convo_id_from_wx_oa(user_id=user_id)
        if force or self.redis.get(convo_id) is None:
            chatbot = self.get_chat_bot()
            chatbot.reset(convo_id=convo_id)
        self.redis.set(convo_id, "1", ex=self.session_expire)

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
    
    async def draw(self, desc: str) -> Optional[str]:
        if not desc:
            return None
        try:
            chatbot = self.get_chat_bot()
            return chatbot.draw(prompt=desc)
        except Exception as err:
            print(err)
            print(traceback.format_exc())
            return None

    def get_chat_bot(self) -> Chatbot:
        return self.__chatbot

    async def chat(self, event: Event, prompt: Optional[str]) -> Optional[str]:
        if not prompt:
            return None
        try:
            convo_id = self.get_convo_id_from_session(event=event)
            chatbot = self.get_chat_bot()
            await self.reset_chat(convo_id=convo_id, force=False)
            reply = chatbot.ask(prompt, convo_id=convo_id)
            await self.reset_expire(convo_id=convo_id)
            return reply
        except Exception as err:
            print(err)
            print(traceback.format_exc())
            return None
        
    async def wx_oa_chat(self, user_id: str, prompt: Optional[str]) -> Optional[str]:
        if not prompt:
            return None
        try:
            convo_id = self.get_convo_id_from_wx_oa(user_id=user_id)
            chatbot = self.get_chat_bot()
            await self.wx_oa_reset_chat(user_id=user_id, force=False)
            print(chatbot.conversation[convo_id])
            reply = await chatbot.ask(prompt, convo_id=convo_id)
            print(reply)
            return reply
        except Exception as err:
            print(err)
            print(traceback.format_exc())
            return None


