import pytest


@pytest.mark.parametrize("entity_name", ('audits', 'team-management'))
@pytest.mark.vcr()
def test_metadata(client, entity_name):
    res = client.get('frontegg/metadata?entityName={}'.format(entity_name))

    assert res.status_code == 200


@pytest.mark.vcr()
def test_send_audits_through_proxy(client):
    res = client.post('frontegg/audits',
                      json={"username": "test", "severity": "Info"})

    assert res.status_code == 201


@pytest.mark.vcr()
def test_send_audits(frontegg):
    result = frontegg.send_audits({"username": "test", "severity": "Info"})
    assert result['username'] == 'test'
    assert result['severity'] == 'Info'
    assert result['tenantId'] == 'my-tenant-id'
