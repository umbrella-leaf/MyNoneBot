import httpx
from typing import Union
from urllib.parse import urlencode
from datetime import datetime
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent as QQGroupMessageEvent,
    MessageEvent as QQMessageEvent
)
import json
import base64
from typing import Optional, Tuple, List


Event = Union[QQMessageEvent, QQGroupMessageEvent]

def get_rest_seconds() -> int:
    """
    获取今天剩余时间（秒数）
    :return: 今天剩余秒数
    """
    now = datetime.now()
    return 24 * 60 * 60 - ((now.hour * 60 + now.minute) * 60 + now.second)


class JhApi:
    def __init__(self, api, new_api, api_key, draw_max_per_day, redis_cli):
        self.api = api
        self.new_api = new_api
        self.api_key = api_key
        self.draw_max_per_day = draw_max_per_day
        self.redis = redis_cli
        self.client = httpx.AsyncClient(timeout=None)
        self.key_prefix = "draw"

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

    async def draw(self, desc: str, event: Event) -> str:
        params = {
            "key": self.api_key,
            "tag": desc,
            "type": "json"
        }
        url = f"{self.new_api}/tuapi?{urlencode(params)}"
        # 修改redis中储存的当天作画次数
        convo_id = self.get_convo_id_from_session(event=event)
        today_draw_times = self.redis.get(convo_id)
        # 没有则储存
        if not today_draw_times:
            self.redis.set(convo_id, 1, ex=get_rest_seconds())
        else:
            # 超出限制则回复警告
            if int(today_draw_times) >= self.draw_max_per_day:
                return f"今日您画图达到最大限制：{self.draw_max_per_day}次！"
            self.redis.set(convo_id, int(today_draw_times) + 1, ex=get_rest_seconds())
        res = await self.client.get(url)
        img = json.loads(res.content)["data"]["img"]
        img = img[img.find("base64") + 7:]
        return f"base64://{img}"
    
    async def fortune(self, constellation: str) -> Optional[str]:
        constellations = [
            "水瓶", "双鱼", "白羊", "金牛", "双子", "巨蟹",
            "狮子", "处女", "天秤", "天蝎", "射手", "摩羯",
            "水瓶座", "双鱼座", "白羊座", "金牛座", "双子座", "巨蟹座",
            "狮子座", "处女座", "天秤座", "天蝎座", "射手座", "摩羯座",
        ]
        if constellation not in constellations:
            return None
        params = {
            "key": self.api_key,
            "msg": constellation
        }
        url = f"{self.api}/xzyst/xzyst?{urlencode(params)}"
        res = await self.client.get(url)
        res = base64.b64encode(res.content).decode()
        return f"base64://{res}"
    
    async def news(self) -> str:
        params = {
            "key": self.api_key
        }
        url = f"{self.api}/60s/60s?{urlencode(params)}"
        res = await self.client.get(url)
        res = base64.b64encode(res.content).decode()
        return f"base64://{res}"
    
    async def background(self, typ: str) -> Tuple[Optional[str], Optional[List[str]]]:
        typ_list = [
            "美女", "爱情", "风景", "清新", "动漫", "明星", "萌宠", "游戏",
            "汽车", "时尚", "日历", "影视", "军事", "体育", "萌娃", "格言"
        ]
        if typ not in typ_list:
            return None, typ_list
        params = {
            "key": self.api_key,
            "msg": typ
        }
        url = f"{self.api}/bztdq/bztdq?{urlencode(params)}"
        res = await self.client.get(url)
        return res.text, None