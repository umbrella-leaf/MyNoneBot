from .data_source import *
from nonebot import get_driver, ReverseDriver
from nonebot.drivers import URL, Request, Response, HTTPServerSetup
from urllib.parse import urlparse, parse_qs
import hashlib


async def handle_get(request: Request) -> Response:
    # step1: 获取url参数
    params = parse_qs(urlparse(str(request.url)).query)
    signature = get_params(params, "signature")
    timestamp = get_params(params, "timestamp")
    nonce = get_params(params, "nonce")
    echostr = get_params(params, "echostr")
    token = "Pvzheroes125"

    if not(signature and timestamp and nonce and echostr):
        return Response(200, content="not a valdation!")

    # step2: 加密生成hashcode
    param_list = [token, timestamp, nonce]
    param_list.sort()
    param_str = "".join(param_list)
    sha1 = hashlib.sha1(param_str.encode("utf-8"))
    hashcode = sha1.hexdigest()

    # step3: 对比生成的hashcode和签名是否相等
    if hashcode == signature:
        return Response(200, content=echostr)
    else:
        return Response(200, content="valid fail!")
    

async def handle_post(request: Request) -> Response:
    webData = request.content
    # print(webData)
    # 后台打日志
    recMsg = receive.parse_xml(webData)
    try:
        if isinstance(recMsg, receive.TextMsg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            MsgId = recMsg.MsgId
            # print(recMsg.Content)
            # content = "test"
            bot_nickname = recMsg.Content[0:2] if len(recMsg.Content) >= 4 else None
            if "重置" in recMsg.Content:
                if is_txBot(bot_nickname):
                    await txBot.wx_oa_reset_chat(user_id=toUser, force=True)
                else:
                    await chatBot.wx_oa_reset_chat(user_id=toUser, force=True)
                content = "您的对话已重置！"
            else:
                if MsgId not in response_dict:
                    response_dict[MsgId] = None
                    if is_txBot(bot_nickname):
                        content = await txBot.wx_oa_chat(user_id=toUser, prompt=recMsg.Content[3:])
                    else:
                        prompt = recMsg.Content[3:] if is_chatBot(bot_nickname) else recMsg.Content
                        content = await chatBot.wx_oa_chat(user_id=toUser, prompt=prompt)
                    response_dict[MsgId] = content
                else:
                    while True:
                        if response_dict[MsgId]:
                            break
                    content = response_dict[MsgId]
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return Response(200, content=replyMsg.send())
        else:
            print("暂不处理")
            return Response(200, content="success")
    except Exception as e:
        print(e)
        return Response(200, content="success")


driver = get_driver()
if isinstance(driver, ReverseDriver):
    driver.setup_http_server(
        HTTPServerSetup(
            path=URL("/"),
            method="GET",
            name="wx_oa_get",
            handle_func=handle_get,
        )
    )
    driver.setup_http_server(
        HTTPServerSetup(
            path=URL("/"),
            method="POST",
            name="wx_oa_post",
            handle_func=handle_post,
        )
    )