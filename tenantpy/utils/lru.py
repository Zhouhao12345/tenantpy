import abc
from typing import Type, Dict, Generic, TypeVar
from collections.abc import MutableMapping
import threading


class Token(abc.ABC):

    def __hash__(self):
        return self.hash()

    def __eq__(self, other: "Token"):
        return self.hash() == other.hash()

    @abc.abstractmethod
    def hash(self):
        raise NotImplementedError


class Element(abc.ABC):

    def __del__(self):
        self.discard()

    @abc.abstractmethod
    def discard(self):
        raise NotImplementedError


token = TypeVar("token", bound=Token)
element = TypeVar("element", bound=Element)


class Pair(Generic[token, element]):
    __slots__ = (
        "prev", "next", "key", "result"
    )

    def __init__(
        self,
        prev: 'Pair',
        next_v: 'Pair',
        key: token,
        result: element,
    ):
        self.prev: 'Pair' = prev
        self.next: 'Pair' = next_v
        self.key: token = key
        self.result: element = result

    def discard(self):
        self.result.discard()


class LRU(MutableMapping, Generic[token, element]):
    __slots__ = ("lock", "root", "max_size")
    cache_map: Dict[token, Pair] = {}
    pair: Type[Pair] = Pair

    @abc.abstractmethod
    def apply(self, key: token) -> element:
        raise NotImplementedError

    def __init__(
        self,
        max_size: int,
    ):
        self.lock = threading.RLock()
        self.max_size = max_size
        self.root: Pair = None

    def set_root(self, root_pair: Pair):
        if root_pair.key == self.root.key:
            return
        if root_pair.key == self.root.prev.key:
            self.root = root_pair
            return
        last = self.root.prev
        old_prev = root_pair.prev
        old_next = root_pair.next
        old_prev.next = old_next
        old_next.prev = old_prev
        self.root.prev = last.next = root_pair
        root_pair.next = self.root
        root_pair.prev = last
        self.root = root_pair

    def __getitem__(self, key: token) -> element:
        with self.lock:
            try:
                old_pair = self.cache_map[key]
                self.set_root(old_pair)
                return old_pair.result
            except KeyError:
                result = self.apply(key)
                self[key] = result
                return result

    def __setitem__(self, key: token, result: element) -> None:
        with self.lock:
            if len(self.cache_map) < self.max_size:
                new_pair = self.pair(
                    prev=None,
                    next_v=None,
                    key=key,
                    result=result,
                )
                if not self.root:
                    self.root = new_pair
                    self.root.prev = self.root
                    self.root.next = self.root
                else:
                    last = self.root.prev
                    new_pair.prev = last
                    new_pair.next = self.root
                    last.next = self.root.prev = new_pair
                    self.root = new_pair
            else:
                last = self.root.prev
                self.root = last
                del self.cache_map[last.key]
                last.key = key
                last.result = result
                new_pair = last
            self.cache_map[key] = new_pair

    def __delitem__(self, result: element) -> None:
        ...

    def __len__(self):
        return len(self.cache_map)

    def __iter__(self) -> Pair:
        yield self.root
        current_pair = self.root.next
        while current_pair.key != self.root.key:
            yield current_pair
            current_pair = current_pair.next

    def __repr__(self):
        tmp = ""
        for result in self:
            tmp += ">" + str(result)
        return tmp
