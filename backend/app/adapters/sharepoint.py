from __future__ import annotations

from app.adapters.base import ResourceCheckResult
from app.models.batch import Resource


def check_site(resource: Resource) -> ResourceCheckResult:
    if not resource.target_identifier:
        return ResourceCheckResult(
            status="BLOCKED", code="SITE_MAPPING_MISSING", severity="BLOCKING",
            message=f"No target SharePoint/OneDrive site mapping found for '{resource.source_identifier}'.",
            tool="Get-SPOSite",
            raw_output=(f"Get-SPOSite -Identity <mapped-site-url>\nWARNING: No target site found for source object '{resource.source_identifier}'.\nCategoryInfo          : ObjectNotFound: ({resource.source_identifier}:String) [Get-SPOSite]\nFullyQualifiedErrorId : Request_ResourceNotFound"),
        )
    if "warn" in resource.display_name.lower():
        return ResourceCheckResult(
            status="WARNING", code="STORAGE_QUOTA_LOW", severity="WARNING",
            message=f"Target site storage quota for '{resource.target_identifier}' is below the recommended threshold.",
            tool="Get-SPOSite",
            raw_output=(f"Get-SPOSite -Identity {resource.target_identifier}\nStorageQuota    : 1024 MB\nStorageUsageCurrent : 980 MB"),
        )
    return ResourceCheckResult(
        status="READY", code=None, severity=None,
        message=f"Site mapping verified for '{resource.target_identifier}'.",
        tool="Get-SPOSite",
        raw_output=f"Get-SPOSite -Identity {resource.target_identifier}\nStatus : Active\nLocked : False",
    )
