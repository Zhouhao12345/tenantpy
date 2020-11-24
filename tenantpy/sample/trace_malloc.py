import os
import gc
import signal
import enum
import tracemalloc
import linecache

__all__ = ["register_snapshot_signal"]

__old_snapshot = None


@enum.unique
class MallocEnvsKey(str, enum.Enum):
    python_trace_malloc = "PYTHONTRACEMALLOC"
    statics_key = "MALLOCSTATISTICKEY"
    statics_rank_number = "MALLOCSTATISTICRANKNUMBER"


@enum.unique
class MallocStatisticsKey(str, enum.Enum):
    traceback = 'traceback'
    filename = 'filename'
    lineno = 'lineno'


def __get_configs(key: MallocEnvsKey):
    return os.environ.get(key.value)


def take_snapshot(sig, frame=None):
    global __old_snapshot
    gc.collect()
    if not __old_snapshot:
        print(f"Start SnapShot Tracking")
        tracemalloc.start()
    snapshot = tracemalloc.take_snapshot()
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
        tracemalloc.Filter(False, "*linecache.py"),
    ))
    key = __get_configs(MallocEnvsKey.statics_key)
    rank_num = __get_configs(MallocEnvsKey.statics_rank_number)
    top_stats = snapshot.statistics(key)
    __old_snapshot = snapshot
    if not top_stats:
        return
    print(f"Top {rank_num}:")
    for index, stat in enumerate(top_stats[:int(rank_num)], 1):
        frame = stat.traceback[0]
        print("#%s: %s:%s: %.1f KiB"
              % (index, frame.filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)


def register_snapshot_signal():
    signal.signal(signal.SIGTTOU, take_snapshot)
