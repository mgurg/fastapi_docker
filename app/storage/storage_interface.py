from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageInterface(ABC):
    @abstractmethod
    def upload_file(self, file_obj: BinaryIO, destination_path: str) -> bool:
        pass

    @abstractmethod
    def download_file(self, file_path: str) -> BinaryIO:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> list:
        pass

    @abstractmethod
    def get_url(self, file_path: str, expiration: int = 3600) -> str:
        pass