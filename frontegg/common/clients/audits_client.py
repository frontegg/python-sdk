from typing import Optional, TypedDict, List
from typing_extensions import  NotRequired
from enum import Enum
from .http_client import HttpClient


class Severity(str, Enum):
    INFO = 'Info'
    MEDIUM = 'Medium',
    HIGH = 'High',
    CRITICAL = 'Critical'
    ERROR = 'Error'


class Audit(TypedDict):
    action: NotRequired[str]
    createdAt: str
    description: NotRequired[str]
    email: NotRequired[str]
    frontegg_id: str
    ip: NotRequired[str]
    severity: Severity
    tenantId: str
    updatedAt: str
    vendorId: str


class SendAuditData(TypedDict):
    severity: Severity


class GetAuditsResponse(TypedDict):
    data: List[Audit]
    total: int


class GetAuditStatsResponse(TypedDict):
    severeThisWeek: int
    totalToday: int


def get_params(count, query_filter, filters, offset, sort_by, sort_direction):
    if not filters:
        filters = {}

    return {
        **filters,
        **{
            'filter': query_filter,
            'sortBy': sort_by,
            'sortDirection': sort_direction,
            'offset': offset,
            'count': count
        }
    }


class AuditsClient:
    def __init__(self, client: HttpClient):
        self.client = client

    def get_audits_v2(
            self, tenant_id: str, count: int, offset: int, *,
            created_from: Optional[str] = None,
            created_to: Optional[str] = None,
            tenant_ids: Optional[List[str]] = None,
            users: Optional[List[str]] = None,
            email: Optional[List[str]] = None,
            sort_by: Optional[str] = None,
            sort_direction: Optional[str] = None,
            query_filter: Optional[str] = None,
            feature_flag_id: Optional[str] = None) -> dict:
        """Retrieve one page of audit logs using the v2 structured filters.

        ``count`` must be between 1 and 200 and ``offset`` must be nonnegative.
        Date filters use ISO 8601 strings. Pagination and filters are validated
        by the API. The response JSON is returned unchanged.
        """
        params = {
            'count': count,
            'offset': offset,
            'created_from': created_from,
            'created_to': created_to,
            'tenant_ids': tenant_ids,
            'users': users,
            'email': email,
            'sortBy': sort_by,
            'sortDirection': sort_direction,
            'filter': query_filter,
            'featureFlagId': feature_flag_id,
        }
        response = self.client.get(
            url='resources/audits/v2',
            params={
                key: value for key, value in params.items()
                if value is not None
            },
            tenant_id=tenant_id,
        )
        response.raise_for_status()
        return response.json()

    def send_audit(self, audit: SendAuditData, tenant_id: str) -> dict:
        """Create new audit.

        :param tenant_id:
        :param audit: A dictionary containing the audit
        :raises requests.HTTPError: If the Frontegg API responds with an HTTP error code, this exception is raised.
        :return: The newly created audit object
        """
        response = self.client.post(
            data=audit,
            tenant_id=tenant_id
        )
        response.raise_for_status()

        return response.json()
