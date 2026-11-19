"""Assert rendered logs never contain authentication material."""
import asyncio
import io
import logging
from unittest.mock import AsyncMock, Mock

import pytest

from frontegg.common.identity_mixin import IdentityClientMixin
from frontegg.common.async_identity_mixin import IdentityAsyncClientMixin
from frontegg.helpers.logger import logger


@pytest.mark.parametrize('is_async', [False, True])
@pytest.mark.parametrize('fails', [False, True])
def test_decode_logs_are_safe(
        is_async,
        fails,
        make_jwt,
        public_key,
        monkeypatch,
        fake_vendor_session):
    cls = IdentityAsyncClientMixin if is_async else IdentityClientMixin
    client = cls(Mock(client_id='client', api_key='test-key'))
    monkeypatch.setattr(
        client, 'get_public_key', AsyncMock(
            return_value=public_key) if is_async else Mock(
            return_value=public_key))
    token = make_jwt({'email': 'private-claim@example.test'})
    if fails:
        def fail(*args, **kwargs):
            raise ValueError('private-error-token')
        module = ('frontegg.common.async_identity_mixin' if is_async
                  else 'frontegg.common.identity_mixin')
        monkeypatch.setattr(module + '.jwt.decode', fail)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    try:
        def decode():
            result = client.decode_jwt('Bearer ' + token)
            return asyncio.run(result) if is_async else result
        if fails:
            with pytest.raises(ValueError):
                decode()
        else:
            assert decode()['email'] == 'private-claim@example.test'
        output = stream.getvalue()
        assert token not in output
        assert 'private-claim' not in output
        assert 'private-error-token' not in output
        diagnostic = ('last retry attempt' if fails
                      else 'jwt was decoded successfully')
        assert diagnostic in output
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)


@pytest.mark.parametrize('is_async', [False, True])
def test_malformed_token_log_is_safe(
        is_async,
        fake_vendor_session,
        monkeypatch,
        caplog):
    cls = IdentityAsyncClientMixin if is_async else IdentityClientMixin
    client = cls(Mock(client_id='client', api_key='test-key'))
    monkeypatch.setattr(
        client, 'get_public_key', AsyncMock(
            return_value='public') if is_async else Mock(
            return_value='public'))
    resolver = Mock()
    resolver.should_handle.return_value = True
    resolver.validate_token = AsyncMock(
        return_value={}) if is_async else Mock(return_value={})
    prefix = ('_IdentityAsyncClientMixin' if is_async
              else '_IdentityClientMixin')
    setattr(client, prefix + '__tokenResolvers', [resolver])

    class MalformedToken:
        def __str__(self):
            return 'private-malformed-token'

    result = client.validate_identity_on_token(MalformedToken())
    if is_async:
        result = asyncio.run(result)
    assert result == {}
    assert 'Failed to extract token' in caplog.text
    assert 'private-malformed-token' not in caplog.text


@pytest.mark.parametrize('is_async', [False, True])
def test_public_key_failure_log_is_safe(
        is_async,
        fake_vendor_session,
        monkeypatch,
        caplog):
    cls = IdentityAsyncClientMixin if is_async else IdentityClientMixin
    client = cls(Mock(client_id='client', api_key='test-key'))
    failure = RuntimeError('private-request-authorization')
    monkeypatch.setattr(
        client, 'fetch_public_key', AsyncMock(
            side_effect=failure) if is_async else Mock(
            side_effect=failure))
    monkeypatch.setattr(
        'frontegg.common.async_identity_mixin.asyncio.sleep', AsyncMock())
    result = client.get_public_key()
    if is_async:
        result = asyncio.run(result)
    assert result is None
    assert 'retry number - 10' in caplog.text
    assert 'failed to get public key in all retries' in caplog.text
    assert 'private-request-authorization' not in caplog.text
