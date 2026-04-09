from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SendEmailParams:
    from_: str
    to: str | list[str]
    subject: str
    html: str | None = None
    text: str | None = None
    reply_to: str | None = None
    cc: str | list[str] | None = None
    bcc: str | list[str] | None = None
    tags: dict[str, str] | None = None
    scheduled_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "from": self.from_,
            "to": self.to,
            "subject": self.subject,
        }
        if self.html is not None:
            d["html"] = self.html
        if self.text is not None:
            d["text"] = self.text
        if self.reply_to is not None:
            d["replyTo"] = self.reply_to
        if self.cc is not None:
            d["cc"] = self.cc
        if self.bcc is not None:
            d["bcc"] = self.bcc
        if self.tags is not None:
            d["tags"] = self.tags
        if self.scheduled_at is not None:
            d["scheduledAt"] = self.scheduled_at
        return d


@dataclass
class Email:
    id: str
    from_: str
    to: list[str]
    subject: str
    status: str
    created_at: str
    html: str | None = None
    text: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Email:
        return cls(
            id=data["id"],
            from_=data["from"],
            to=data["to"],
            subject=data["subject"],
            status=data["status"],
            created_at=data["createdAt"],
            html=data.get("html"),
            text=data.get("text"),
        )


@dataclass
class Domain:
    id: str
    name: str
    status: str
    records: list[dict[str, Any]]
    created_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Domain:
        return cls(
            id=data["id"],
            name=data["name"],
            status=data.get("status", "pending"),
            records=data.get("records", data.get("dns_records", [])),
            created_at=data.get("createdAt", data.get("created_at", "")),
        )


@dataclass
class ApiKey:
    id: str
    name: str
    permission: str
    created_at: str
    key: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApiKey:
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            permission=data.get("permission", data.get("key_permission", "")),
            created_at=data.get("createdAt", data.get("created_at", "")),
            key=data.get("key"),
        )


@dataclass
class Webhook:
    id: str
    url: str
    events: list[str]
    created_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Webhook:
        return cls(
            id=data["id"],
            url=data.get("url", ""),
            events=data.get("events", []),
            created_at=data.get("createdAt", data.get("created_at", "")),
        )


@dataclass
class Template:
    id: str
    name: str
    created_at: str
    subject: str | None = None
    html: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Template:
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            created_at=data.get("createdAt", data.get("created_at", "")),
            subject=data.get("subject"),
            html=data.get("html"),
        )


@dataclass
class MetricsDataPoint:
    timestamp: str
    sent: int
    delivered: int
    opened: int
    clicked: int
    bounced: int
    complained: int


@dataclass
class Metrics:
    sent: int
    delivered: int
    opened: int
    clicked: int
    bounced: int
    complained: int
    timeseries: list[MetricsDataPoint] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Metrics:
        ts = [
            MetricsDataPoint(**point) for point in data.get("timeseries", [])
        ]
        return cls(
            sent=data["sent"],
            delivered=data["delivered"],
            opened=data["opened"],
            clicked=data["clicked"],
            bounced=data["bounced"],
            complained=data["complained"],
            timeseries=ts,
        )
