import redis

from ..backend import context


class CacheMetaData(redis.Redis):

    def discard(self):
        self.connection_pool.disconnect()


class CacheMetaDataBuilder(context.MetaDataBuilder[CacheMetaData]):

    __slots__ = ("config",)

    def __init__(self, **config):
        self.config = config

    def hash(self) -> int:
        return self.config.__str__().__hash__()

    def build(self) -> CacheMetaData:
        if "url" in self.config:
            return CacheMetaData.from_url(
                url=self.config["url"]
            )
        return CacheMetaData(**self.config)
