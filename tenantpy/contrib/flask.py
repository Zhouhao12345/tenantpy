import abc
import peewee
import contextlib
import atexit
import flask
import opentracing

try:
    from dbutils import steady_db
except ImportError:
    from DBUtils import SteadyDB as steady_db


from ..utils import proxy
from ..backend import (
    context,
    mysql,
    cache,
)
from ..settings import ConfigPartition
from ..sample import jaeger

__all__ = ["ConfigManager", "BaseModel", "init_jaeger", "init_app"]


class ConfigManager(abc.ABC):
    @abc.abstractmethod
    def get_config(self, key: ConfigPartition) -> dict:
        raise NotImplementedError


class PoolMysqlDatabase(peewee.MySQLDatabase):

    def __init__(self, connect: steady_db.SteadyDBConnection, *args, **kwargs):
        self.connect_ = connect
        super(PoolMysqlDatabase, self).__init__(*args, **kwargs)

    def sequence_exists(self, seq):
        pass

    def _connect(self):
        return self.connect_


class BaseModel(peewee.Model):
    class Meta:
        database = proxy.LocalProxy(flask.g, "database")


tenant_envs = context.TenantEnvironments(max_size=10)


@atexit.register
def shut_down_db_pool():
    tenant_envs.close()


@contextlib.contextmanager
def build_context(token: context.TenantToken):
    tenant_item = tenant_envs[token]
    try:
        flask.g.database = PoolMysqlDatabase(
            connect=tenant_item.databasemetadata.connection(),
            database=token,
        )
        flask.g.redis = tenant_item.cachemetadata
        yield None
    except BaseException as e:
        raise e
    finally:
        flask.g.database.close()
        flask.g.redis.close()


def init_jaeger(
    app: flask.Flask,
    config_manager: ConfigManager,
):
    jaeger.init_tracer(config_manager.get_config(ConfigPartition.jaeger))

    def before_request():
        request = flask.request
        span_context = opentracing.tracer.extract(
            format=opentracing.Format.HTTP_HEADERS,
            carrier=dict(request.headers),
        )
        flask.g.jaeger_scope = opentracing.tracer.start_active_span(
            request.url.path,
            child_of=span_context)

    def after_request(response: flask.Response):
        headers_data = dict(response.headers)
        opentracing.tracer.inject(
            span_context=flask.g.jaeger_scope.span.context,
            format=opentracing.Format.HTTP_HEADERS,
            carrier=headers_data,
        )
        for key, value in headers_data.items():
            response.headers.add(_key=key, _value=value)
        flask.g.jaeger_scope.close()
        del flask.g.jaeger_scope

    app.before_request(before_request)
    app.after_request(after_request)


def init_app(
    app: flask.Flask,
    config_manager: ConfigManager,
):

    def before_request():
        mysql_config = config_manager.get_config(ConfigPartition.mysql)
        redis_config = config_manager.get_config(ConfigPartition.redis)
        token = context.TenantToken()
        token.organize(mysql.DataBaseMetaDataBuilder(**mysql_config))
        token.organize(cache.CacheMetaDataBuilder(**redis_config))
        tenant_item = tenant_envs[token]
        flask.g.database = PoolMysqlDatabase(
            connect=tenant_item.databasemetadata.connection(),
            database=token,
        )
        flask.g.redis = tenant_item.cachemetadata

    def after_request(response: flask.Response):
        flask.g.database.close()
        del flask.g.database
        del flask.g.redis
        return response

    app.before_request(before_request)
    app.after_request(after_request)
