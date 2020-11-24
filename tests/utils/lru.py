import random
from ...tenantpy.utils import lru
import unittest
from pympler import asizeof


class MyToke(lru.Token):
    def __init__(self, id_: int):
        self.id_ = id_

    def hash(self):
        return hash(self.id_)

    def __repr__(self):
        return str(self.id_)


class MyElement(lru.Element):
    def __init__(self, id_: int):
        self.switch = True
        self.id_ = id_

    def discard(self):
        self.switch = False

    def __repr__(self):
        return str(self.id_)


class MyPair(lru.Pair[MyToke, MyElement]):
    def __repr__(self):
        return f"{self.key}:{self.result}"


class MyLRU(lru.LRU[MyToke, MyElement]):
    pair = MyPair

    def apply(self, key: MyToke) -> MyElement:
        return MyElement(id_=key.id_)


class TestLRU(unittest.TestCase):

    def test_1_add(self):
        lru_ins = MyLRU(max_size=10)
        for i in range(1, 5):
            lru_ins[MyToke(i)] = MyElement(i)
            asizeof.asizeof(lru_ins)
        for _ in range(1000):
            token_num = random.choice([_ for _ in range(1, 5)])
            lru_ins[MyToke(token_num)]
            print(asizeof.asizeof(lru_ins))
