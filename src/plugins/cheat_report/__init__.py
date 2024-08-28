from nonebot import on
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    GroupMessageEvent,
    GroupUploadNoticeEvent
)
from typing import Union

from .common import upload_report, redis_cli
from .config import plugin_config

Bot = Union[QQBot]
Event = Union[GroupMessageEvent, GroupUploadNoticeEvent]

cheaterReportGroupId = plugin_config.listen_group_numbers


async def is_cheater_record_group(event: Event) -> bool:
    if str(event.group_id) not in cheaterReportGroupId:
        return False
    if isinstance(event, GroupMessageEvent):
        message = str(event.get_message())
        if message == '':
            # 消息体为空，则一定是群文件上传的前一条空消息，在redis中记录
            redis_cli.set(event.user_id, event.message_id, ex=86400)
            return False
    return True


cheaterRecord = on(rule=is_cheater_record_group, priority=18, block=True)


@cheaterRecord.handle()
async def handle_cheater_report(bot: Bot, event: Event):
    await upload_report(event, bot)
    await cheaterRecord.finish()


