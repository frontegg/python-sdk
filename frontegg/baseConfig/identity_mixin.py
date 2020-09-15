from abc import ABCMeta, abstractmethod
from frontegg.helpers.frontegg_urls import frontegg_urls
import typing
import jwt
import requests


class IdentityClientMixin(metaclass=ABCMeta):
    __publicKey = None

    @property
    @abstractmethod
    def vendor_session_request(self) -> requests.Session:
        pass

    def get_public_key(self) -> str:
        if self.__publicKey:
            return self.__publicKey

        response = self.vendor_session_request.get(frontegg_urls.identity_service['vendor_config'])
        data = response.json()
        self.__publicKey = data.get('publicKey')
        return self.__publicKey

    def decode_jwt(self, authorization_header, verify: typing.Optional[bool] = True):
        if not authorization_header:
            raise Exception('Authorization headers is missing')
        jwt_token = authorization_header.replace('Bearer ', '')
        if verify:
            public_key = self.get_public_key()
            decoded = jwt.decode(jwt_token, public_key, algorithms='RS256')
        else:
            decoded = jwt.decode(jwt_token, algorithms='RS256', verify=False)
        return decoded
