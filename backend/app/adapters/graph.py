from __future__ import annotations

from app.adapters.base import ResourceCheckResult
from app.models.batch import Resource


def check_identity(resource: Resource) -> ResourceCheckResult:
    if not resource.target_identifier:
        return ResourceCheckResult(
            status="BLOCKED", code="GROUP_MAPPING_MISSING", severity="BLOCKING",
            message=f"No target Entra ID group/user mapping found for '{resource.source_identifier}'.",
            tool="Get-MgGroupMember",
            raw_output=(f"Get-MgGroupMember -GroupId <mapped-group>\nWARNING: No corresponding target identity found for source object '{resource.source_identifier}'.\nCategoryInfo          : ObjectNotFound: ({resource.source_identifier}:String) [Get-MgGroupMember]\nFullyQualifiedErrorId : Request_ResourceNotFound"),
        )
    if "warn" in resource.display_name.lower():
        return ResourceCheckResult(
            status="WARNING", code="LICENSE_MISMATCH", severity="WARNING",
            message=f"Target license SKU for '{resource.target_identifier}' does not match the source assignment.",
            tool="Get-MgUserLicenseDetail",
            raw_output=(f"Get-MgUserLicenseDetail -UserId {resource.target_identifier}\nSkuPartNumber : ENTERPRISEPACK (source) vs SPE_E3 (target)\nStatus        : Mismatch -- manual license reconciliation recommended."),
        )
    return ResourceCheckResult(
        status="READY", code=None, severity=None,
        message=f"Identity mapping verified for '{resource.target_identifier}'.",
        tool="Get-MgUser",
        raw_output=f"Get-MgUser -UserId {resource.target_identifier}\nAccountEnabled : True\nUserType       : Member",
    )
