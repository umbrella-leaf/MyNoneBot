import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


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
