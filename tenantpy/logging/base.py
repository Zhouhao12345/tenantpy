import logging


class BaseLogger(logging.Logger):
    namespace = "tenant"

    def __init__(self, name, level=logging.NOTSET):
        base_class = self.__class__
        names = []
        for base in reversed(base_class.__mro__):
            namespace = getattr(base, "namespace", None)
            if namespace:
                names.append(namespace)
        names.append(name)
        super().__init__(".".join(names), level=level)
