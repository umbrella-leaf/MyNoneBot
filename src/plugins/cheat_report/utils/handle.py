import re
import json
from uuid import uuid4
from src.plugins.cheat_report.data_source import file_saver
from pydantic import BaseModel
from typing import List, Dict, Any
from nonebot.compat import type_validate_python
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    GroupMessageEvent,
    GroupUploadNoticeEvent
)


async def handle_at(segment: MessageSegment):
    return segment.data["name"]


async def handle_multimedia(segment: MessageSegment):
    resource_url = segment.data["url"]
    resource_name = segment.data.get("filename", None)
    if resource_name is None:
        resource_name = f"{uuid4().hex}.mp4"
    resource_url = await file_saver.save_file(resource_name, resource_url)
    return resource_url


async def handle_face(segment: MessageSegment):
    return str(segment)


emoji_text_reg = re.compile(r'\[.*?]')


async def handle_text(segment: MessageSegment):
    text = segment.data["text"]
    text = re.sub(emoji_text_reg, '', text)
    if text == "" or str(text).startswith("/"):
        return None
    return text


class ForwardMessage(BaseModel):
    user_id: str
    nickname: str
    content: List[MessageSegment]

    async def serialize(self) -> Dict[str, Any]:
        message = {
            "avatar_url": f"https://q1.qlogo.cn/g?b=qq&nk={self.user_id}&s=640",
            "nickname": self.nickname,
            "segments": []
        }
        for segment in self.content:
            if segment.type == "at":
                message["segments"].append(await handle_at(segment))
            elif segment.type == "image" or segment.type == "video":
                message["segments"].append(await handle_multimedia(segment))
            elif segment.type == "face":
                message["segments"].append(await handle_face(segment))
            elif segment.type == "text":
                text = await handle_text(segment)
                if text is not None:
                    message["segments"].append(text)
        return message


async def handle_forward(segment: MessageSegment, bot: Bot, event: GroupMessageEvent):
    forward_id = segment.data['id']
    response = await bot.get_forward_msg(id=forward_id)
    forward_msgs = []
    for node in response['message']:
        forward_msg = type_validate_python(
            ForwardMessage, node['data']
        )
        forward_msgs.append(await forward_msg.serialize())
    forward_file_name = f"{event.message_id}.forward"
    forward_content = json.dumps(forward_msgs, indent=4)
    return await file_saver.save_file(forward_file_name, forward_content)


async def handle_group_file(bot: Bot, event: GroupUploadNoticeEvent):
    group_id = event.group_id
    file_id = event.file.id
    resource_name = event.file.name
    busid = event.file.busid
    resource_url = (await bot.get_group_file_url(group_id=group_id, file_id=file_id, busid=busid))["url"]
    return await file_saver.save_file(resource_name, resource_url)
