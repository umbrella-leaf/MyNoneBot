import os
import re
import datetime
import httpx
from uuid import uuid4
from typing import Dict, Any, Union
from nonebot import require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GroupUploadNoticeEvent


Event = Union[GroupMessageEvent, GroupUploadNoticeEvent]

require("QQGuild")
from src.plugins.QQGuild import dbclient

resource_path = "https://report.umbrella-leaf.com"
temp_group_file_path = "/root/.config/QQ/NapCat/temp"
image_suffix = ["jpg", "png"]
video_suffix = ["mp4"]
resource_types = ["video", "image"]


async def get_member_user_info(event: Event, bot: Bot) -> Dict[str, Any]:
    group_id = event.group_id
    user_id = event.user_id
    user_info = await bot.get_group_member_info(group_id=group_id,
                                                user_id=user_id,
                                                no_cache=False)
    user_info["avatar_url"] = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    return user_info


async def acquire_resources(name: str, url: str):
    resource_name, resource_suffix = name.split(".")
    resource_type = "image" if resource_suffix in image_suffix else "video"
    resource_name += f".{resource_type}"
    for folder in resource_types:
        os.makedirs(f"resources/{folder}s", exist_ok=True)

    save_path = f"{resource_type}s/{resource_name}"
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        with open(f"resources/{save_path}", "wb") as fw:
            fw.write(response.content)
    return f"{resource_path}/{save_path}"


async def extract_appendices(event: Event, bot: Bot):
    mentions = []
    appendices = []
    message = ""
    if isinstance(event, GroupMessageEvent):
        raw_message = event.get_message()
        for segment in raw_message:
            if segment.type == "at":
                mention_id = segment.data["qq"]
                mention_info = await bot.get_group_member_info(group_id=event.group_id,
                                                               user_id=mention_id,
                                                               no_cache=False)
                mention_username = mention_info["nickname"]
                mentions.append(f"@{mention_username}")
            elif segment.type in resource_types:
                resource_url = segment.data["url"]
                resource_name = segment.data.get("filename", None)
                if resource_name is None:
                    resource_name = f"{uuid4().hex}.mp4"
                resource_url = await acquire_resources(resource_name, resource_url)
                appendices.append(resource_url)
            elif segment.type == 'face':
                message += str(segment)
            elif segment.type == "text":
                text = segment.data["text"]
                if re.match(r'^\[.*?]$', text):
                    continue
                message += segment.data["text"]
    else:
        group_id = event.group_id
        file_id = event.file.id
        resource_name = event.file.name
        busid = event.file.busid
        resource_url = (await bot.get_group_file_url(group_id=group_id, file_id=file_id, busid=busid))["url"]
        resource_url = await acquire_resources(resource_name, resource_url)
        appendices.append(resource_url)
    message = " ".join(mentions) + message
    appendix_urls = " ".join(appendices)
    return message, appendix_urls


async def upload_report(event: Event, bot: Bot):
    user_info = await get_member_user_info(event, bot)
    nickname = user_info["nickname"]
    avatar_url = user_info["avatar_url"]
    send_time = event.time
    message, appendix_urls = await extract_appendices(event, bot)
    # 时间戳转换为具体时间
    formatted_time = datetime.datetime.fromtimestamp(send_time).strftime('%Y-%m-%d %H:%M:%S')
    dbclient.addInfo(
        nickname=nickname,
        avatar_url=avatar_url,
        message=message,
        appendix=appendix_urls,
        send_time=formatted_time
    )
