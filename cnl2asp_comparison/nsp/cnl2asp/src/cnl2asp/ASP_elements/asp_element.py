from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cnl2asp.ASP_elements.asp_atom import ASPAtom


class ASPElement:
    def get_atom_list(self) -> list[ASPAtom]:
        return []

