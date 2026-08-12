from __future__ import annotations

from app.adapters.base import ResourceCheckResult
from app.models.batch import Resource


def check_mailbox(resource: Resource) -> ResourceCheckResult:
    if not resource.target_identifier:
        return ResourceCheckResult(
            status="BLOCKED", code="TARGET_MAILUSER_INVALID", severity="BLOCKING",
            message=f"Target MailUser is invalid or missing for '{resource.source_identifier}'.",
            tool="Get-MailUser",
            raw_output=(f"Get-MailUser -Identity '{resource.source_identifier}'\nWARNING: The object '{resource.source_identifier}' was not found.\n    + CategoryInfo          : ObjectNotFound: ({resource.source_identifier}:String) [Get-MailUser], ManagementObjectNotFoundException\n    + FullyQualifiedErrorId : [Server=EXCH01] Microsoft.Exchange.Management.Tasks.Get-MailUser"),
        )
    if "warn" in resource.display_name.lower():
        return ResourceCheckResult(
            status="WARNING", code="FORWARDING_ENABLED", severity="WARNING",
            message=f"Mail forwarding is enabled on '{resource.target_identifier}' and will not migrate automatically.",
            tool="Get-Mailbox",
            raw_output=(f"Get-Mailbox -Identity {resource.target_identifier}\nForwardingSmtpAddress      : external@partner.com\nDeliverToMailboxAndForward : True"),
        )
    return ResourceCheckResult(
        status="READY", code=None, severity=None,
        message=f"Mailbox '{resource.target_identifier}' is ready for migration.",
        tool="Get-Mailbox",
        raw_output=(f"Get-Mailbox -Identity {resource.target_identifier}\nRecipientTypeDetails     : UserMailbox\nProhibitSendReceiveQuota : 100 GB"),
    )
