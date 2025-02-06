from typing import TypeVar
from ._entity_base import EntityBase

__all__ = ["TEntity"]

TEntity = TypeVar("TEntity", bound=EntityBase)
