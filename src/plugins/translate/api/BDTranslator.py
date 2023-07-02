import json
import httpx
from random import randint
from hashlib import md5
from urllib import parse


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