import json
import httpx
from random import randint
from hashlib import md5
from urllib import parse
import execjs


class BaiduTranslator:
    def __init__(self, appid: str, secret_key: str):
        self.base_url = "http://api.fanyi.baidu.com/api/trans/vip"
        self.appid = appid
        self.secret_key = secret_key
        self.salt = ''
        self.sign = ''
        self.client = httpx.AsyncClient(timeout=True)

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
        param = parse.urlencode(data)
        url = f"{self.base_url}/translate?{param}"

        res = await self.client.get(url=url)
        return json.loads(res.text)['trans_result'][0]['dst']


class BaiduPublicTranslator:
    def __init__(self, sign_generate_js: str, acs_token: str, cookie: str):
        self.base_url = "https://fanyi.baidu.com"
        self.sign_generate_js = sign_generate_js
        self.acs_token = acs_token
        self.cookie = cookie
        self.client = httpx.AsyncClient(timeout=None)

    def generate_sign(self, text: str):
        sign = execjs.compile(self.sign_generate_js).call("e", text)
        return sign

    async def lang_detect(self, text: str):
        url = f"{self.base_url}/langdetect"
        res = await self.client.post(
            url=url,
            data={
                "query": text
            }
        )
        return json.loads(res.text)["lan"]

    @staticmethod
    def lang_choice(lan: str):
        if lan == "zh":
            return "zh", "en"
        return "en", "zh"

    async def translate(self, text: str):
        sign = self.generate_sign(text=text)
        from_lan, to_lan = self.lang_choice(
            lan=await self.lang_detect(text=text)
        )
        params = {
            "from": from_lan,
            "to": to_lan,
            "query": text,
            "transtype": "translang",
            "simple_means_flag": "3",
            "sign": sign,
            "token": "2ebec4ea4428f385ad2b8dbaa9102727"
        }
        headers = {
            "Acs-Token": self.acs_token,
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/73.0.3683.86 Safari/537.36"
        }
        url = f"{self.base_url}/v2transapi"
        res = await self.client.post(
            url=url,
            data=params,
            headers=headers
        )
        return json.loads(res.text)["trans_result"]["data"][0]["dst"]