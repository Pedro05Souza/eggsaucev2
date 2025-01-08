from typing import Generic, TypeVar


T = TypeVar("T")

__all__ = ["ImmutableProxy"]


class ImmutableProxy(Generic[T]):
    def __init__(self, obj: T):
        self._obj = obj

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def __setattr__(self, name, value):
        if name == "_obj":
            super().__setattr__(name, value)
            return
        raise AttributeError("This object is read-only.")

    def __repr__(self):
        return f"<ImutableProxy {self._obj}>"


class MutableProxy(Generic[T]):
    def __init__(self, obj: T):
        self._obj = obj
        self._is_updated_required = False
        self._modified_fields = {}

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def __setattr__(self, name, value):
        if name in {"_obj", "_is_updated_required", "_modified_fields"}:
            super().__setattr__(name, value)
            return

        if getattr(self._obj, name) != value:
            self._is_updated_required = True
            self._modified_fields[name] = value

    def __repr__(self):
        return f"<MutableProxy {self._obj}>"

    @property
    def is_updated_required(self):
        return self._is_updated_required

    @property
    def modified_fields(self):
        return self._modified_fields

    @property
    def obj(self):
        return self._obj
