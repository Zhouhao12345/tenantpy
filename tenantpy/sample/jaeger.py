import functools
import inspect
import jaeger_client
import atexit
import opentracing
from opentracing.scope_managers import contextvars


def close_tracer():
    opentracing.tracer.close()


def init_tracer(config: dict):
    config = jaeger_client.Config(
        config=config,
        validate=True,
        scope_manager=contextvars.ContextVarsScopeManager(),
        service_name=config["service_name"],
    )
    global_tracer = config.new_tracer()
    opentracing.set_global_tracer(global_tracer)
    atexit.register(close_tracer)


def trace(span_name: str, **tags):
    def inner(func):
        def _normal_func():
            return opentracing.tracer.start_active_span(
                span_name,
                child_of=opentracing.tracer.active_span,
            )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with _normal_func() as scope:
                for tag_key, tag_value in tags.items():
                    scope.span.set_tag(tag_key, tag_value)
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with _normal_func() as scope:
                for tag_key, tag_value in tags.items():
                    scope.span.set_tag(tag_key, tag_value)
                return func(*args, **kwargs)

        if not inspect.iscoroutinefunction(func):
            return sync_wrapper
        return async_wrapper
    return inner
