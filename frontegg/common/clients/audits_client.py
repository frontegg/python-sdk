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
