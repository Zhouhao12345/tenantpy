import enum


@enum.unique
class ConfigPartition(str, enum.Enum):
    mysql = "mysql"
    redis = "redis"
    jaeger = "jaeger"
