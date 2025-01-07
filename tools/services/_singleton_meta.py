from threading import Lock

class SingletonMeta(type):
    _instance = None
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
            return cls._instance
