from frontegg.common.cache.cache_manager import CacheManager
from frontegg.common.cache.cache_manager import SetOptions
from typing import List, Optional, Type, Generic, TypeVar, Tuple, Dict
from frontegg.common.package_utils import PackageUtils
import json

T = TypeVar('T')


class RedisCacheManager(Generic[T], CacheManager[T]):
    def __init__(self, options):
        redis = PackageUtils.load_package('redis')
        self.cache = redis.Redis(host=options.get('host'), port=options.get('port'), db=options.get('db'), password=options.get('password'))

    def set(self, key: str, data: Type[T], options: Optional[SetOptions] = None) -> None:
        self.cache.set(key, json.dumps(data, indent=4))
        if options and options.get('expires_in_seconds'):
            self.cache.expire(key, options.get('expires_in_seconds'))

    def get(self, key: str) -> Optional[Type[T]]:
        data = self.cache.get(key)
        if data is not None:
            return json.loads(data)

        return None

    def delete(self, keys: List[str]) -> None:
        for key in keys:
            if key in self.cache:
                del self.cache[key]
