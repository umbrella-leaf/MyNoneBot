import xml.etree.ElementTree as ET


def parse_xml(web_data: str):
    if len(web_data) == 0:
        return None
    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    if msg_type == 'text':
        return TextMsg(xmlData)


class Msg:
    def __init__(self, xmlData: ET.Element):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class TextMsg(Msg):
    def __init__(self, xmlData: ET.Element):
        super().__init__(xmlData=xmlData)
        self.Content = xmlData.find('Content').text


class ImageMsg(Msg):
    def __init__(self, xmlData):
        super().__init__(xmlData=xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text
