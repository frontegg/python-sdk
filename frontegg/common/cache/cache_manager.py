import abc
from typing import List, Optional, Type, Generic, TypeVar


class SetOptions:
    expires_in_seconds: Optional[int]


T = TypeVar('T')


class CacheManager(Generic[T], abc.ABC):
    @abc.abstractmethod
    def set(self, key: str, data: Type[T], options: Optional[SetOptions] = None) -> None:
        pass

    @abc.abstractmethod
    def get(self, key: str) -> Optional[Type[T]]:
        pass

    @abc.abstractmethod
    def delete(self, keys: List[str]) -> None:
        pass
