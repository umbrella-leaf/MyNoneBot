import datetime
import json
from typing import Dict, Any, Union, List

from nonebot import require
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    GroupUploadNoticeEvent)
from nonebot.adapters.onebot.v11.event import Reply
from nonebot.compat import type_validate_python

from .data_source import file_saver
from .utils.handle import (
    handle_at,
    handle_multimedia,
    handle_face,
    handle_text,
    handle_forward,
    handle_group_file
)

Event = Union[GroupMessageEvent, GroupUploadNoticeEvent]

require("QQGuild")
require("ai_chat")
from src.plugins.QQGuild import dbclient
from src.plugins.ai_chat.data_source import redis_cli


async def get_member_user_info(event: Event, bot: Bot) -> Dict[str, Any]:
    group_id = event.group_id
    user_id = event.user_id
    user_info = await bot.get_group_member_info(group_id=group_id,
                                                user_id=user_id,
                                                no_cache=False)
    user_info["avatar_url"] = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    return user_info


async def get_reply_details(reply_id: int):
    reply_details = {k.decode('utf-8'): v.decode('utf-8') for k, v in redis_cli.hgetall(reply_id).items()}
    reply_details["segments"] = eval(reply_details["segments"])
    return reply_details


async def recursive_handle_reply(event: Event, bot: Bot) -> str:
    if isinstance(event, GroupMessageEvent):
        reply = event.reply
        if reply is None:
            return ""
        first_reply_id = reply.message_id
        reply_chains = {}
        while reply is not None:
            message_id = reply.message_id
            reply_chains[message_id] = await get_reply_details(message_id)
            if reply.message.count("reply") <= 0:
                break
            reply_id = int(reply.message[0].data['id'])
            reply = type_validate_python(
                Reply, await bot.get_msg(message_id=reply_id)
            )
            reply_chains[message_id]["reply_id"] = reply.message_id
        reply_chains["reply_id"] = first_reply_id
        reply_file_name = f"{event.message_id}.reply"
        reply_content = json.dumps(reply_chains, indent=4)
        return await file_saver.save_file(reply_file_name, reply_content)
    return ""


async def save_message_to_redis(event: Event, segments: List[str], nickname: str, avatar_url: str, formatted_time: str):
    user_id = event.user_id
    message_id = event.message_id if hasattr(event, "message_id") else int(redis_cli.get(user_id).decode("utf-8"))
    redis_cli.hset(message_id, "nickname", nickname)
    redis_cli.hset(message_id, "avatar_url", avatar_url)
    redis_cli.hset(message_id, "send_time", formatted_time)
    redis_cli.hset(message_id, "segments", str(segments))
    redis_cli.expire(message_id, 86400)


def append_element_to_lists(element: Any, *lists: List[List]):
    for lst in lists:
        lst.append(element)


async def extract_appendices(event: Event, bot: Bot):
    mentions = []
    appendices = []
    message = ""
    segments = []
    if isinstance(event, GroupMessageEvent):
        raw_message = event.get_message()
        for segment in raw_message:
            if segment.type == "at":
                mention_username = await handle_at(segment)
                append_element_to_lists(mention_username, mentions, segments)
            elif segment.type == 'image' or segment.type == 'video':
                resource_url = await handle_multimedia(segment)
                append_element_to_lists(resource_url, appendices, segments)
            elif segment.type == 'face':
                face = await handle_face(segment)
                message += face
                segments.append(face)
            elif segment.type == "text":
                text = await handle_text(segment)
                if text is None:
                    continue
                message += text
                segments.append(text)
            elif segment.type == 'forward':
                resource_url = await handle_forward(segment, bot, event)
                append_element_to_lists(resource_url, appendices, segments)
    else:
        resource_url = await handle_group_file(bot, event)
        append_element_to_lists(resource_url, appendices, segments)
    message = " ".join(mentions) + message
    return message, appendices, segments


async def upload_report(event: Event, bot: Bot):
    user_info = await get_member_user_info(event, bot)
    nickname = user_info["card"] if "card" in user_info else user_info["nickname"]
    avatar_url = user_info["avatar_url"]
    send_time = event.time
    reply_file_url = await recursive_handle_reply(event, bot)
    message, appendices, segments = await extract_appendices(event, bot)
    if reply_file_url != "":
        appendices.append(reply_file_url)
    appendix_urls = " ".join(appendices)
    # 时间戳转换为具体时间
    formatted_time = datetime.datetime.fromtimestamp(send_time).strftime('%Y-%m-%d %H:%M:%S')
    await save_message_to_redis(event, segments, nickname, avatar_url, formatted_time,)
    dbclient.addInfo(
        nickname=nickname,
        avatar_url=avatar_url,
        message=message,
        appendix=appendix_urls,
        send_time=formatted_time
    )

