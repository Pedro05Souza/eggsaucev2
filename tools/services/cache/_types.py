from __future__ import annotations
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from entities import BaseEntity


KT = TypeVar("KT")
VT = TypeVar("VT")
TE = TypeVar("TE", bound="BaseEntity") # pylint: disable=invalid-name
