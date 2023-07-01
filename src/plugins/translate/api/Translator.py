import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

import httpx
from random import randint
from hashlib import md5
from urllib import parse


class TencentTranslator:
    def __init__(self, secret_id: str, secret_key: str):
        # 初始化客户端
        cred = credential.Credential(
            secret_id=secret_id,
            secret_key=secret_key
        )
        # 实例化一个http选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = 'tmt.tencentcloudapi.com'
        # 实例化一个client选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象
        self.client = tmt_client.TmtClient(cred, "ap-shanghai", clientProfile)

    async def translate(self, text: str):
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.TextTranslateRequest()
            params = {
                "SourceText": text,
                "Source": "auto",
                "Target": "zh",
                "ProjectId": 0
            }
            req.from_json_string(json.dumps(params))
            # 返回的resp是一个TextTranslateResponse的实例，与请求对象对应
            resp = self.client.TextTranslate(req)
            return resp.TargetText
        except TencentCloudSDKException as e:
            print(e)
            return None


class BaiduTranslator:
    def __init__(self, appid: str, secret_key: str):
        self.appid = appid
        self.secret_key = secret_key
        self.salt = ''
        self.sign = ''

    def generate_salt(self, num: int):
        self.salt = ''
        for i in range(0, num):
            self.salt += str(randint(1, 9))

    def generate_sign(self, q: str):
        self.sign = ''
        self.sign = self.appid + q + self.salt + self.secret_key
        self.sign = md5(self.sign.encode(encoding="UTF8")).hexdigest()

    async def translate(self, text: str):
        self.generate_salt(8)
        self.generate_sign(q=text)
        data = {
            "q": text,
            "from": "auto",
            "to": "zh",
            "appid": self.appid,
            "salt": self.salt,
            "sign": self.sign
        }
        base_url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
        param = parse.urlencode(data)
        url = f"{base_url}?{param}"

        client = httpx.AsyncClient(timeout=None)
        res = await client.get(url=url)
        return json.loads(res.text)['trans_result'][0]['dst']
