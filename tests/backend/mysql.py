import unittest
import random
import threading
from concurrent.futures import thread
import peewee as og_peewee

from tenantpy.backend import (
    cache,
    mysql,
    context,
)
from tenantpy.contrib import flask


class User(flask.BaseModel):
    englishName = og_peewee.CharField()


config_1 = dict(
    host="0.0.0.0",
    port=3306,
    password="foo1",
    user="foo1",
    database="foo1",
)

config_2 = dict(
    host="0.0.0.0",
    port=3306,
    password="bar1",
    user="bar1",
    database="bar1",
)


config_3 = dict(
    url="redis://0.0.0.0:6380/0",
)


config_4 = dict(
    url="redis://0.0.0.0:6380/1",
)


class TestTenantDB(unittest.TestCase):

    def test_single(self):
        request()

    def test_mutil_thread_connect(self):
        with thread.ThreadPoolExecutor(max_workers=100) as t:
            for _ in range(1000):
                t.submit(request)

    def test_thread_local(self):
        with thread.ThreadPoolExecutor(max_workers=2) as t:
            for _ in range(100):
                t.submit(increase)


class SafeMutex(threading.local):
    def __init__(self):
        self.__dict__.update({
            "number": 0
        })


safe_mutex = SafeMutex()


def increase():
    safe_mutex.number += 1


def request():
    db_config = random.choice([config_1, config_2])
    cache_config = random.choice([config_3, config_4])
    token = context.TenantToken()
    token.organize(mysql.DataBaseMetaDataBuilder(**db_config))
    token.organize(cache.CacheMetaDataBuilder(**cache_config))
    with flask.build_context(token):
        ins = User.get()
        try:
            if db_config["database"] == "gllueweb_ats":
                assert ins.englishName == "Admin"
            elif db_config["database"] == "test_gllueweb_ats":
                assert ins.englishName == "123"
        except AssertionError:
            print(f"assert error {ins.englishName}")
