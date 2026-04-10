"""ApprovalGate: human-in-the-loop approval workflow."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalTicket:
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: str | None = None
    rejection_reason: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    resolved_at: str | None = None


class ApprovalGate:
    def __init__(self) -> None:
        self._tickets: dict[str, ApprovalTicket] = {}

    def request_approval(self, request: dict[str, Any]) -> ApprovalTicket:
        ticket = ApprovalTicket(request=request)
        self._tickets[ticket.ticket_id] = ticket
        return ticket

    def approve(self, ticket_id: str, approver: str) -> ApprovalTicket | None:
        ticket = self._tickets.get(ticket_id)
        if ticket and ticket.status == ApprovalStatus.PENDING:
            ticket.status = ApprovalStatus.APPROVED
            ticket.approver = approver
            ticket.resolved_at = datetime.now(timezone.utc).isoformat()
        return ticket

    def reject(
        self, ticket_id: str, approver: str, reason: str = ""
    ) -> ApprovalTicket | None:
        ticket = self._tickets.get(ticket_id)
        if ticket and ticket.status == ApprovalStatus.PENDING:
            ticket.status = ApprovalStatus.REJECTED
            ticket.approver = approver
            ticket.rejection_reason = reason
            ticket.resolved_at = datetime.now(timezone.utc).isoformat()
        return ticket

    def status(self, ticket_id: str) -> ApprovalStatus | None:
        ticket = self._tickets.get(ticket_id)
        return ticket.status if ticket else None

    def get_ticket(self, ticket_id: str) -> ApprovalTicket | None:
        return self._tickets.get(ticket_id)
