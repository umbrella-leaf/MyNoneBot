from .object import *
from pond import Pond, PooledObject, PooledObjectFactory
from .config import plugin_config
from typing import Tuple


class PooledNeteaseFactory(PooledObjectFactory):
    def creatInstantce(self) -> PooledObject:
        netease = NeteaseMusic(
            search_api=plugin_config.netease_search_api,
            song_api=plugin_config.netease_song_api,
            cookie=plugin_config.netease_cookie
        )
        return PooledObject(netease)

    def destroy(self, pooled_object: PooledObject) -> None:
        del pooled_object

    def reset(self, pooled_object: PooledObject) -> PooledObject:
        pooled_object.keeped_object.songs = []
        return pooled_object

    def validate(self, pooled_object: PooledObject) -> bool:
        return pooled_object.keeped_object.validate_result

    # def __del__(self):
    #     pond.clear(factory)


pond = Pond(borrowed_timeout=2,
            time_between_eviction_runs=-1,
            thread_daemon=True,
            eviction_weight=0.8)
factory = PooledNeteaseFactory(pooled_maxsize=10, least_one=False)
pond.register(factory)


async def borrowNeteaseObject() -> Tuple[NeteaseMusic, PooledObject]:
    pooled_object: PooledObject = await pond.async_borrow(factory)
    netease: NeteaseMusic = pooled_object.use()
    return netease, pooled_object


async def recycleNeteaseObject(pooled_object: PooledObject):
    await pond.async_recycle(pooled_object, factory)

