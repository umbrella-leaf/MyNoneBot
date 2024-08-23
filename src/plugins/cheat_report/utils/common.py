import os
import datetime
import httpx
from typing import Dict, Any
from nonebot import require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

require("QQGuild")
from src.plugins.QQGuild import dbclient


resource_path = "https://report.umbrella-leaf.com"
image_suffix = ["jpg", "png"]
video_suffix = ["mp4"]
resource_types = ["video", "image"]


async def get_member_user_info(event: GroupMessageEvent, bot: Bot) -> Dict[str, Any]:
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
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        with open(f"resources/{save_path}", "wb") as fw:
            fw.write(response.content)
    return f"{resource_path}/{save_path}"


async def extract_appendices(event: GroupMessageEvent, bot: Bot):
    mentions = []
    appendices = []
    message = ""
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
            resource_name = segment.data["file"]
            resource_url = await acquire_resources(resource_name, resource_url)
            appendices.append(resource_url)
        elif segment.type == "text":
            message = segment.data["text"].strip()
    if message != "":
        mentions.append(message)
    message = " ".join(mentions)
    appendix_urls = " ".join(appendices)
    return message, appendix_urls


async def upload_report(event: GroupMessageEvent, bot: Bot):
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

