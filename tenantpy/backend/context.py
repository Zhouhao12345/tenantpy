import abc
from typing import Dict, List, Generic, TypeVar

from ..utils import (
    lru,
)


class MetaData(abc.ABC):

    @abc.abstractmethod
    def discard(self):
        raise NotImplementedError


metadata = TypeVar("metadata", bound=MetaData)


class MetaDataBuilder(abc.ABC, Generic[metadata]):

    def build(self) -> metadata:
        raise NotImplementedError

    def __hash__(self):
        return self.hash()

    def __eq__(self, other: "MetaDataBuilder"):
        return self.hash() == other.hash()

    @abc.abstractmethod
    def hash(self) -> str:
        raise NotImplementedError


class TenantContext(lru.Element):

    __slots__ = ("__meta_map",)

    def __init__(self):
        self.__meta_map: Dict[str, MetaData] = {}

    def inject(self, meta_data: MetaData):
        self.__meta_map.update({
            type(meta_data).__name__.lower(): meta_data
        })

    def __getattr__(self, item):
        return self.__meta_map[item]

    def discard(self):
        for meta_data in self.__meta_map.values():
            meta_data.discard()


class TenantToken(lru.Token):

    __slots__ = ("__builders",)

    def __init__(self):
        self.__builders: List[MetaDataBuilder] = []

    def organize(self, meta_builder: MetaDataBuilder):
        self.__builders.append(meta_builder)

    def hash(self) -> int:
        return tuple([
            _.hash() for _ in self.__builders
        ]).__hash__()

    def build_context(self) -> TenantContext:
        tenant_context = TenantContext()
        for builder in self.__builders:
            tenant_context.inject(builder.build())
        return tenant_context


class TenantPair(lru.Pair[TenantToken, TenantContext]):
    def __repr__(self):
        return f"{self.key}:{self.result}"

    def discard(self):
        self.result.discard()


class TenantEnvironments(lru.LRU[TenantToken, TenantContext]):
    pair = TenantPair

    def apply(self, key: TenantToken) -> TenantContext:

        return key.build_context()

    def close(self):
        with self.lock:
            if not self.cache_map.__len__():
                return
            context_item: TenantPair
            for context_item in self:
                if not context_item:
                    continue
                context_item.discard()


