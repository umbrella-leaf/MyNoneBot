from DouBaoChat.bot import ChatBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from .base_bot import *
from typing import Optional
import traceback


class DouBaoBot(Bot):
    def __init__(
            self,
            api_key: str,
            redis_cli,
            key_prefix: str,
            session_expire: int,
            model: Optional[str] = None,
            bot_id: Optional[str] = None,
    ):
        self._chatbot = ChatBot(
            api_key=api_key,
            endpoint=model,
            bot_id=bot_id
        )
        self._redis = redis_cli
        self._key_prefix = key_prefix
        self._session_expire = session_expire

    def get_chat_bot(self) -> ChatBot:
        return self._chatbot

    async def reset_chat(self, convo_id: str, force: bool):
        if force or self._redis.get(convo_id) is None:
            chatbot = self.get_chat_bot()
            chatbot.reset(convo_id=convo_id)
        # 提问前，即使对话过期，也不重设过期时间，而是等到回答结束才重设，但如果强制重置则立即重设过期时间
        if force:
            await self.reset_expire(convo_id)

    def get_convo_id_from_session(self, event: Event) -> str:
        user_id = 'user'
        if isinstance(event, MessageEvent) or isinstance(event, GroupMessageEvent):
            user_id = event.user_id
            user_id = str(user_id)
        group_id = "personal"
        if isinstance(event, GroupMessageEvent):
            group_id = event.group_id
            group_id = str(group_id)
        return f"{self._key_prefix}-{group_id}-{user_id}"

    async def chat(self, event: Event, prompt: Optional[str]) -> Optional[str]:
        if not prompt:
            return None
        try:
            convo_id = self.get_convo_id_from_session(event=event)
            chatbot = self.get_chat_bot()
            await self.reset_chat(convo_id=convo_id, force=False)
            reply = await chatbot.ask(message=prompt, convo_id=convo_id)
            await self.reset_expire(convo_id=convo_id)
            return reply
        except Exception as err:
            print(err)
            print(traceback.format_exc())
            return None

    async def reset_expire(self, convo_id: str):
        self._redis.set(convo_id, "1", ex=self._session_expire)
