from frontegg.common.cache.cache_manager import CacheManager
from frontegg.common.cache.cache_manager import SetOptions
from typing import List, Optional, Type, Generic, TypeVar, Tuple, Dict
from time import time

T = TypeVar('T')


class LocalCacheManager(Generic[T], CacheManager[T]):
    def __init__(self):
        self.cache: Dict[str, Tuple[Type[T], float]] = {}

    def set(self, key: str, data: Type[T], options: Optional[SetOptions] = None) -> None:
        if options and options.get('expires_in_seconds'):
            self.cache[key] = (data, time() + options.get('expires_in_seconds'))
        else:
            self.cache[key] = data

    def get(self, key: str) -> Optional[Type[T]]:
        if key in self.cache:
            if isinstance(self.cache[key], tuple):
                if time() > self.cache[key][1]:
                    del self.cache[key]
                    return None
                else:
                    return self.cache[key][0]
            else:
                return self.cache[key]
        else:
            return None

    def delete(self, keys: List[str]) -> None:
        for key in keys:
            if key in self.cache:
                del self.cache[key]
