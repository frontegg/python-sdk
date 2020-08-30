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
def test_get_audits_stats_through_proxy(client):
    res = client.get('frontegg/audits/stats')

    assert res.status_code == 200


@pytest.mark.vcr()
def test_send_audits(frontegg):
    result = frontegg.send_audits({"username": "test", "severity": "Info"})
    assert result['username'] == 'test'
    assert result['severity'] == 'Info'
    assert result['tenantId'] == 'my-tenant-id'


@pytest.mark.vcr()
def test_get_audits(frontegg):
    result = frontegg.get_audits('my-tenant-id', count=5)
    expected = {'data': [
        {'__v': 0, '_id': '5de7d4bf7df94f75b9f2db8c', 'status': 'Archived', 'userId': 'user1', 'severity': 'Info',
         'tenantId': 'my-tenant-id', 'vendorId': 'my-client-id',
         'createdAt': '2019-12-04 17:46:07.958', 'updatedAt': '2019-12-04T15:46:07.958Z',
         'notificationId': '5de3fe56565a6480147f120a'}, {'ip': '1.2.3.4', '__v': 0, '_id': '5df541f9c9740de059440db7',
                                                         'time': 'Sat Dec 14 2019 22:11:38 GMT+0200 (Israel Standard Time)',
                                                         'resource': 'Portal', 'severity': 'Info',
                                                         'tenantId': 'my-tenant-id',
                                                         'vendorId': 'my-client-id',
                                                         'createdAt': '2019-12-14 22:11:37.432',
                                                         'updatedAt': '2019-12-14T20:11:37.432Z'},
        {'ip': '1.2.3.4', '__v': 0, '_id': '5df540b9c9740d6fbc440da9',
         'time': 'Sat Dec 14 2019 22:06:18 GMT+0200 (Israel Standard Time)', 'resource': 'Portal', 'severity': 'Info',
         'tenantId': 'my-tenant-id', 'vendorId': 'my-client-id',
         'createdAt': '2019-12-14 22:06:17.473', 'updatedAt': '2019-12-14T20:06:17.473Z'}, {
            'ip': '1.2.3.4', '__v': 0, '_id': '5df54087c9740d7369440da4',
            'time': 'Sat Dec 14 2019 22:05:28 GMT+0200 (Israel Standard Time)', 'resource': 'Portal',
            'severity': 'Info', 'tenantId': 'my-tenant-id', 'vendorId': 'my-client-id',
            'createdAt': '2019-12-14 22:05:27.420', 'updatedAt': '2019-12-14T20:05:27.420Z'},
        {'ip': '1.2.3.4', '__v': 0, '_id': '5df54452c9740d6458440dca',
         'time': 'Sat Dec 14 2019 22:21:39 GMT+0200 (Israel Standard Time)', 'resource': 'Portal', 'severity': 'Info',
         'tenantId': 'my-tenant-id', 'vendorId': 'my-client-id',
         'createdAt': '2019-12-14 22:21:38.714', 'updatedAt': '2019-12-14T20:21:38.714Z'}], 'total': 71}
    assert result == expected


@pytest.mark.vcr()
def test_get_audit_stats(frontegg):
    result = frontegg.get_audit_stats('my-tenant-id')
    assert result == {'totalToday': 2, 'severeThisWeek': 0}


@pytest.mark.vcr()
def test_get_audits_metadata(frontegg):
    result = frontegg.get_audits_metadata()
    expected = {'rows': [{'_id': '5d3d2ee54a04a50033da91df', 'entityName': 'audits', 'properties': [
        {'_id': '5d3d2ee54a04a50033da91e6', 'name': 'createdAt', 'displayName': 'Date', 'type': 'Timestamp',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e5', 'name': 'user', 'displayName': 'User', 'type': 'UserIdentity',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e4', 'name': 'resource', 'displayName': 'Resource', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e3', 'name': 'action', 'displayName': 'Action', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': True}, {
            '_id': '5d3d2ee54a04a50033da91e2', 'name': 'severity', 'displayName': 'Severity', 'type': 'AlphaNumeric',
            'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e1', 'name': 'ip', 'displayName': 'IP Address', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e0', 'name': 'message', 'displayName': 'Message', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': False}], 'vendorId': 'my-client-id',
        'id': '39372f0f-1d14-4ecd-8462-1b22d5ca9264', 'createdAt': '2019-07-28T05:13:09.723Z',
        'updatedAt': '2019-07-28T05:13:09.723Z', '__v': 0}]}
    assert result == expected
