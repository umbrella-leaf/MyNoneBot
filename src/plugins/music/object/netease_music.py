import json
import httpx
from urllib.parse import urlencode
from .song_info import SongInfo
from time import time
from typing import List


class NeteaseMusic:
    validate_result: bool = True

    def __init__(self, search_api: str, song_api: str, cookie: str):
        self.search_api = search_api
        self.song_api = song_api
        self.cookie = cookie
        self.songs: list[SongInfo] = []
        self.client = httpx.AsyncClient(timeout=None)

    async def __get_song_infos(self, song_name: str) -> List[SongInfo]:
        params = {
            'keywords': '',
            'timestamp': 0
        }
        search_api = self.search_api
        params['keywords'] = song_name
        params['timestamp'] = int(time())
        params = urlencode(params)
        url = f"{search_api}?{params}"
        res = await self.client.get(url)
        res = json.loads(res.text)
        result = res['result']
        songs = result['songs']

        song_infos = []
        for song in songs:
            song_id = song['id']
            song_name = song['name']
            song_album = song["al"]["name"]
            song_info = SongInfo(song_id=song_id, song_name=song_name, song_album=song_album)
            for singer in song['ar']:
                song_info.singers.append(singer['name'])
            song_infos.append(song_info)
            # 最多八首
            if len(song_infos) == 8:
                break
        return song_infos

    async def get_song_infos(self, song_name: str):
        params = {
            'id': '',
            'level': 'higher',
            'timestamp': 0
        }
        songs = await self.__get_song_infos(song_name)
        song_api = self.song_api
        for song in songs:
            params['id'] = song.sid
            params['timestamp'] = int(time())
            new_params = urlencode(params)
            url = f"{song_api}?{new_params}"
            res = await self.client.post(url, data={"cookie": self.cookie})
            result = json.loads(res.text)
            song.url = result["data"][0]["url"]
        self.songs = songs

    def get_song_list(self) -> str:
        song_list: str = ""
        for idx in range(0, len(self.songs)):
            song = self.songs[idx]
            song_line = f"{idx + 1}. {str(song)}\n"
            song_list += song_line
        song_list = f"为您搜索到如下歌曲，请选择序号：\n{song_list}"
        return song_list