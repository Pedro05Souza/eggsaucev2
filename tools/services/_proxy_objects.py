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
        self.is_update_required = False
        self.modified_fields = {}

    def __getattr__(self, name):
        if name in {"_obj", "is_update_required", "modified_fields"}:
            return self.__dict__[name]

        attr = getattr(self._obj, name)

        if isinstance(attr, (set, list, dict)):
            copied_attr = attr.copy()
            self.modified_fields[name] = copied_attr
            self.is_update_required = True
            # Mark update as required because:
            # 1. This method may not be called again to check states between the original and the copied object.
            # Even if the object reference is held
            # The worst case scenario is another check in the cache services to see if the attributes are equal.
            return copied_attr

        return attr

    def __setattr__(self, name, value):
        if name in {"_obj", "is_update_required", "modified_fields"}:
            super().__setattr__(name, value)
            return

        if isinstance(value, (set, list, dict)):
            super().__setattr__(name, value.copy())
        else:
            super().__setattr__(name, value)

        if getattr(self._obj, name, None) != value:
            self.is_update_required = True
            self.modified_fields[name] = value

    def __repr__(self):
        return f"<MutableProxy {self._obj}>"

    def __call__(self):
        """Return the underlying object."""
        return self._obj

    def __eq__(self, other: T):
        return self._obj == other
