from nonebot import on_message
from nonebot.adapters.onebot.v11 import (
    Bot as QQBot,
    GroupMessageEvent,
    MessageSegment
)
from typing import Union
from .utils.common import upload_report

Bot = Union[QQBot]
Event = Union[GroupMessageEvent]

cheaterReportGroupId = '645832801'


async def is_cheater_record_group(event: Event) -> bool:
    return str(event.group_id) == cheaterReportGroupId


cheaterRecord = on_message(rule=is_cheater_record_group, priority=18, block=True)


@cheaterRecord.handle()
async def handle_cheater_report(bot: Bot, event: Event):
    await upload_report(event, bot)
    await cheaterRecord.finish()

