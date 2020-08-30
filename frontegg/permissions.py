"""Frontegg proxy permissions"""

import typing
from enum import Enum
from urllib.parse import urlsplit


class _Audits(Enum):
    Read = (('GET', '/audits'),)
    Stats = (('GET', '/audits/stats'),)
    Export = (('POST', '/audits/export/pdf'), ('POST', '/audits/export/csv'))


class _Teams(Enum):
    Read = (('GET', '/team'), ('GET', '/team/roles'))
    Stats = (('GET', '/team/stats'),)
    Add = (('POST', '/team'),)
    Update = (('PUT', '/team'),)
    Delete = (('DELETE', '/team'),)
    ResendActivationEmail = (('POST', '/team/resendActivationEmail'),)
    ResetPassword = (('POST', '/team/resetPassword'),)


class FronteggPermissions(Enum):
    """Frontegg permissions enum."""
    All = (('*', '*'),)
    Audits = _Audits
    Teams = _Teams


class ForbiddenRequest(Exception):
    pass


def validate_permissions(endpoint: str, method: str, permissions: typing.List[FronteggPermissions]) -> None:
    if endpoint.startswith('http'):
        _, _, endpoint, _, _ = urlsplit(endpoint)

    if endpoint.endswith('/'):
        endpoint = endpoint.rstrip('/')

    for permission in permissions:
        if any(
                (allowed_method == '*' or method == allowed_method)
                and (allowed_endpoint == '*' or allowed_endpoint == endpoint)
                for allowed_method, allowed_endpoint in permission.value
        ):
            break
    else:
        raise ForbiddenRequest()


__all__ = ('FronteggPermissions', 'validate_permissions', 'ForbiddenRequest')
