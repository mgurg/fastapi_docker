from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):  # pragma: no cover
    OVERWRITE_EXISTING_FILES = True
    """Whether to overwrite existing files
    if the name is the same or add a suffix to the filename."""

    @abstractmethod
    def get_name(self, name: str) -> str:
        ...

    # def get_path(self, name: str) -> str:
    #     ...

    @abstractmethod
    def get_size(self, name: str) -> int:
        ...

    # def open(self, name: str) -> BinaryIO:
    #     ...

    @abstractmethod
    def write(self, file: BinaryIO, name: str) -> str:
        ...

    # def generate_new_filename(self, filename: str) -> str:
    #     ...
