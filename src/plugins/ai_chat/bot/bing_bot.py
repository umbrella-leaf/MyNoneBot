from typing import Union, Dict
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent as QQGroupMessageEvent,
    MessageEvent as QQMessageEvent
)
from .base_bot import *
import traceback
import json
from pprint import pprint


Event = Union[QQMessageEvent, QQGroupMessageEvent]


class NewBingBot(Bot):
    def __init__(self, proxy: str,
                 cookie_path: str,
                 redis_cli,
                 key_prefix: str,
                 session_expire: int):
        self._bot_map: Dict[str, Chatbot] = {}
        self.proxy = proxy
        self.cookie_path = cookie_path
        self.redis = redis_cli
        self.key_prefix = key_prefix
        self.session_expire = session_expire

    async def reset_chat(self, convo_id: str, force: bool):
        if force or self.redis.get(convo_id) is None:
            chatbot = await self.get_chat_bot(convo_id=convo_id)
            await chatbot.reset()
        # 提问前，即使对话过期，也不重设过期时间，而是等到回答结束才重设，但如果强制重置则立即重设过期时间
        if force:
            await self.reset_expire(convo_id)

    async def reset_expire(self, convo_id: str):
        self.redis.set(convo_id, "1", ex=self.session_expire)

    def get_convo_id_from_session(self, event: Event) -> str:
        user_id = "user"
        if isinstance(event, QQMessageEvent) or isinstance(event, QQGroupMessageEvent):
            user_id = event.user_id
            user_id = str(user_id)
        group_id = "personal"
        if isinstance(event, QQGroupMessageEvent):
            group_id = event.group_id
            group_id = str(group_id)
        return f"{self.key_prefix}-{group_id}-{user_id}"

    async def get_chat_bot(self, convo_id: str):
        if convo_id not in self._bot_map:
            cookies = json.loads(open(self.cookie_path, encoding="utf-8").read())
            self._bot_map[convo_id] = await Chatbot.create(cookies=cookies, proxy=self.proxy)
        return self._bot_map[convo_id]

    async def chat(self, event: Event, prompt: Optional[str]) -> Optional[str]:
        if not prompt:
            return None
        try:
            convo_id = self.get_convo_id_from_session(event=event)
            chatbot = await self.get_chat_bot(convo_id=convo_id)
            await self.reset_chat(convo_id=convo_id, force=False)
            res = await chatbot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
            reply = res["adaptive_text"]
            await self.reset_expire(convo_id=convo_id)
            return reply
        except Exception as err:
            print(err)
            print(traceback.format_exc())
            return None
