import logging
from typing import Any
from abc import ABC, abstractmethod

class AdapterRegistry(ABC):

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    @abstractmethod
    def register_adapters(adapters: dict[str, Any]) -> None:
        pass
