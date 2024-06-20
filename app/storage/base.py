from abc import ABC, abstractmethod
from typing import BinaryIO

class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    OVERWRITE_EXISTING_FILES = True

    @abstractmethod
    def get_name(self, name: str) -> str:
        pass

    @abstractmethod
    def get_size(self, name: str) -> int:
        pass

    @abstractmethod
    def write(self, file: BinaryIO, name: str) -> str:
        pass
