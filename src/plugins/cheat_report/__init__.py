from nonebot import on_message, on
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    GroupMessageEvent,
    GroupUploadNoticeEvent,
    MessageSegment
)
from typing import Union
from .utils.common import upload_report

Bot = Union[QQBot]
Event = Union[GroupMessageEvent, GroupUploadNoticeEvent]

cheaterReportGroupId = ['645832801']


async def is_cheater_record_group(event: Event) -> bool:
    if str(event.group_id) not in cheaterReportGroupId:
        return False
    if isinstance(event, GroupMessageEvent):
        message = str(event.get_message())
        if message == '':
            return False
    return True


cheaterRecord = on(rule=is_cheater_record_group, priority=18, block=True)


@cheaterRecord.handle()
async def handle_cheater_report(bot: Bot, event: Event):
    await upload_report(event, bot)
    await cheaterRecord.finish()


