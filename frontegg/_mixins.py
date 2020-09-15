import typing
from abc import ABCMeta, abstractmethod
from urllib.parse import urlsplit, urlunsplit
import jwt
from flask import request


def _get_filters(count, filter, filters, offset, sort_by, sort_direction):
    if not filters:
        filters = {}
    data = filters
    if filter:
        data['filter'] = filter
    if sort_by:
        data['sortBy'] = sort_by
    if sort_direction:
        data['sortDirection'] = sort_direction
    if offset:
        data['offset'] = offset
    if count:
        data['count'] = count
    return data


class AuditsClientMixin(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _config(self) -> dict:
        """A dictionary containing the configuration for Frontegg."""
        pass

    def get_audits(self,
                   tenant_id: typing.Optional[str] = None,
                   filter: typing.Optional[str] = None,
                   sort_by: typing.Optional[str] = None,
                   sort_direction: typing.Optional[str] = None,
                   offset: typing.Optional[int] = None,
                   count: typing.Optional[int] = None,
                   filters: typing.Optional[dict] = None) -> dict:
        """Fetch audit records from the Frontegg API.

        TODO: Document filters and other options with examples.

        :param tenant_id:
        :param filter:
        :param sort_by:
        :param sort_direction:
        :param offset:
        :param count:
        :param filters:
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: A dictionary representing the parsed JSON response.
        """
        data = _get_filters(count, filter, filters, offset,
                            sort_by, sort_direction)

        response = self._client.request(
            self._config['FRONTEGG_AUDITS_SERVICE_URL'],
            'GET',
            params=data,
            tenant_id=tenant_id
        )
        response.raise_for_status()

        return response.json()

    def send_audits(self, audits: dict, tenantId) -> dict:
        """Create new audits.

        :param audits: A dictionary containing the audit.
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: The newly created audit object.
        """
        response = self._client.request(
            self._config['FRONTEGG_AUDITS_SERVICE_URL'],
            'POST',
            json=audits,
            tenant_id=tenantId
        )
        response.raise_for_status()

        return response.json()

    def get_audit_stats(self, tenant_id: str) -> dict:
        """Fetch audit statistics.

        :param tenant_id: The tenant id to fetch the stats for.
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: The audit statistics.
        """
        scheme, network, location, path, query = urlsplit(
            self._config['FRONTEGG_AUDITS_SERVICE_URL'])
        if location.endswith('/'):
            location += 'stats/'
        else:
            location += '/stats/'
        endpoint = urlunsplit((scheme, network, location, path, query))
        response = self._client.request(
            endpoint,
            'GET',
            json={
                'tenantId': tenant_id
            },
            tenant_id=tenant_id
        )
        response.raise_for_status()

        return response.json()

    def get_audits_metadata(self) -> dict:
        """Retrieve metadata for audits.

        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return The metadata for audits.
        """
        response = self._client.request(self._config['FRONTEGG_METADATA_SERVICE_URL'],
                                        'GET',
                                        params={'entityName': 'audits'})
        response.raise_for_status()

        return response.json()

    def set_audits_metadata(self, metadata: dict) -> dict:
        """Set the metadata for audits.

        :param metadata: The new metadata for audits.
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: The newly set metadata for audits.
        """
        response = self._client.request(self._config['FRONTEGG_METADATA_SERVICE_URL'],
                                        'POST',
                                        json=metadata)
        response.raise_for_status()

        return response.json()

    def export_pdf(self,
                   tenant_id: typing.Optional[str] = None,
                   filter: typing.Optional[str] = None,
                   sort_by: typing.Optional[str] = None,
                   sort_direction: typing.Optional[str] = None,
                   offset: typing.Optional[int] = None,
                   count: typing.Optional[int] = None,
                   filters: typing.Optional[dict] = None) -> bytes:
        """Export audit records from the Frontegg API to PDF.

        TODO: Document filters and other options with examples.

        :param tenant_id:
        :param filter:
        :param sort_by:
        :param sort_direction:
        :param offset:
        :param count:
        :param filters:
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: The PDF as a bytes string.
        """
        scheme, network, location, path, query = urlsplit(
            self._config['FRONTEGG_AUDITS_SERVICE_URL'])
        if location.endswith('/'):
            location += 'export/pdf'
        else:
            location += '/export/pdf'
        endpoint = urlunsplit((scheme, network, location, path, query))

        data = _get_filters(count, filter, filters, offset,
                            sort_by, sort_direction)

        response = self._client.request(
            endpoint,
            'get',
            data=data,
            tenant_id=tenant_id
        )
        response.raise_for_status()

        return response.content

    def export_csv(self,
                   tenant_id: typing.Optional[str] = None,
                   filter: typing.Optional[str] = None,
                   sort_by: typing.Optional[str] = None,
                   sort_direction: typing.Optional[str] = None,
                   offset: typing.Optional[int] = None,
                   count: typing.Optional[int] = None,
                   filters: typing.Optional[dict] = None) -> bytes:
        """Export audit records from the Frontegg API to PDF.

        TODO: Document filters and other options with examples.

        :param tenant_id:
        :param filter:
        :param sort_by:
        :param sort_direction:
        :param offset:
        :param count:
        :param filters:
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: The PDF as a bytes string.
        """
        scheme, network, location, path, query = urlsplit(
            self._config['FRONTEGG_AUDITS_SERVICE_URL'])
        if location.endswith('/'):
            location += 'export/csv'
        else:
            location += '/export/csv'
        endpoint = urlunsplit((scheme, network, location, path, query))

        data = _get_filters(count, filter, filters, offset,
                            sort_by, sort_direction)

        response = self._client.request(
            endpoint,
            'get',
            data=data,
            tenant_id=tenant_id
        )
        response.raise_for_status()

        return response.content


class SSOClientMixin(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _config(self) -> dict:
        """A dictionary containing the configuration for Frontegg."""
        pass

    def prelogin(self, payload: str) -> str:
        """
        Perform SSO prelogin phase

        Parameters:
        payload: can be email of tenantId
        """
        response = self._client.request(
            '/'.join([self._config['FRONTEGG_TEAM_SERVICE_URL'],
                      'resources/sso/v1/prelogin']),
            'POST',
            json={'payload': payload}
        )
        return response

    def postlogin(self, saml_response):
        response = self._client.request(
            '/'.join([self._config['FRONTEGG_TEAM_SERVICE_URL'],
                      'resources/sso/v1/postlogin']),
            'POST',
            json=saml_response
        )
        return response.json()


class IdentityClientMixin(metaclass=ABCMeta):
    __publicKey = None

    @property
    @abstractmethod
    def _config(self) -> dict:
        """A dictionary containing the configuration for Frontegg."""
        pass

    def getPublicKey(self) -> str:
        if self.__publicKey:
            return self.__publicKey
        url = '/'.join([self._config['FRONTEGG_IDENTITY_SERVICE_URL'],
                        'resources/configurations/v1'])
        response = self._client.request(
            url,
            'GET'
        )
        data = response.json()
        self.__publicKey = data.get('publicKey')
        return self.__publicKey


    def decode_jwt(self, verify: typing.Optional[bool] = True):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            raise Exception('Authorization headers is missing')
        jwt_token = authorization_header.replace('Bearer ', '')
        if verify:
            public_key = self.getPublicKey()
            decoded = jwt.decode(jwt_token, public_key, algorithms='RS256')
        else:
            decoded = jwt.decode(jwt_token, algorithms='RS256', verify = False)
        request.user = decoded
        return decoded

