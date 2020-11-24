import pymysql

try:
    from dbutils import (
        steady_db,
        pooled_db,
    )
except ImportError:
    from DBUtils import (
        SteadyDB as steady_db,
        PooledDB as pooled_db,
    )


from ..backend import context


class DataBaseMetaData(pooled_db.PooledDB):

    def steady_connection(self):
        return CustomSteadyDBConnect(
            self._creator, self._maxusage, self._setsession,
            self._failures, self._ping, True, *self._args, **self._kwargs)

    def discard(self):
        self.close()


class CustomSteadyDBConnect(steady_db.SteadyDBConnection):

    @property
    def server_version(self):
        return self._con.server_version


class DataBaseMetaDataBuilder(context.MetaDataBuilder[DataBaseMetaData]):

    __slots__ = ("config",)

    def __init__(self, **config):
        self.config = config

    def hash(self) -> int:
        return self.config.__str__().__hash__()

    def build(self) -> DataBaseMetaData:
        return DataBaseMetaData(
            creator=pymysql,
            **self.config,
        )
