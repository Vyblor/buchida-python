from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def unwrap(resp: Any) -> Any:
    """Return the payload of a ``{"data": ...}`` success envelope.

    Responses that are not enveloped are returned unchanged.
    """
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp


class SendResult(dict):  # type: ignore[type-arg]
    """Unwrapped ``emails.send`` response (e.g. ``{"id": "...", "status": "queued"}``).

    Deprecated: ``result["data"]``, ``result.get("data")`` and ``"data" in result`` still
    work (returning the result itself) so code written against the pre-0.2 raw envelope keeps
    working. No warning is emitted; use the result directly.
    """

    def __contains__(self, key: Any) -> bool:
        return key == "data" or super().__contains__(key)

    def __getitem__(self, key: Any) -> Any:
        if key == "data" and not dict.__contains__(self, "data"):
            return self
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        if key == "data" and not dict.__contains__(self, "data"):
            return self
        return super().get(key, default)


class ListResponse(list):  # type: ignore[type-arg]
    """A page of results: a plain ``list`` plus ``cursor`` and ``has_more``.

    ``.data`` is the list itself. Deprecated: the pre-0.2 envelope keys ``res["data"]``,
    ``res["cursor"]``, ``res["hasMore"]`` (and ``.get()``, ``in``, ``.keys()``) still work,
    without warnings. Note ``isinstance(res, dict)`` is False and an empty page is falsy.
    """

    _LEGACY_KEYS: tuple[str, ...] = ("data", "cursor", "hasMore")

    def __init__(
        self,
        items: Any = (),
        cursor: str | None = None,
        has_more: bool = False,
    ):
        super().__init__(items)
        self.cursor = cursor
        self.has_more = has_more

    @property
    def data(self) -> list[Any]:
        return self

    @classmethod
    def from_envelope(cls, resp: Any) -> ListResponse:
        if isinstance(resp, dict):
            return cls(
                resp.get("data") or [],
                resp.get("cursor"),
                bool(resp.get("hasMore", resp.get("has_more", False))),
            )
        return cls(resp or [])

    def _legacy(self, key: str) -> Any:
        if key == "data" and "data" in self._LEGACY_KEYS:
            return self
        if key == "cursor" and "cursor" in self._LEGACY_KEYS:
            return self.cursor
        if key in ("hasMore", "has_more") and "hasMore" in self._LEGACY_KEYS:
            return self.has_more
        raise KeyError(key)

    def keys(self) -> list[str]:
        return list(self._LEGACY_KEYS)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, str) and item in self._LEGACY_KEYS:
            return True
        return super().__contains__(item)

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            return self._legacy(key)
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._legacy(key)
        except KeyError:
            return default


class BatchItem(dict):  # type: ignore[type-arg]
    """One entry of a batch send: ``{"data": {...}}`` on success or ``{"error": {code, message}}``."""

    @property
    def data(self) -> dict[str, Any] | None:
        return self.get("data")

    @property
    def error(self) -> dict[str, Any] | None:
        return self.get("error")

    @property
    def ok(self) -> bool:
        return "error" not in self


class BatchResponse(ListResponse):
    """Per-item results of ``emails.send_batch`` (a list of :class:`BatchItem`).

    Deprecated: ``res["data"]`` / ``res.get("data")`` / ``"data" in res`` still work.
    """

    _LEGACY_KEYS = ("data",)

    @classmethod
    def from_envelope(cls, resp: Any) -> BatchResponse:  # type: ignore[override]
        items = resp.get("data") if isinstance(resp, dict) else resp
        return cls([BatchItem(i) for i in (items or [])])


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
    from_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "from": self.from_,
            "to": self.to,
            "subject": self.subject,
        }
        if self.from_name is not None:
            d["from_name"] = self.from_name
        if self.html is not None:
            d["html"] = self.html
        if self.text is not None:
            d["text"] = self.text
        if self.reply_to is not None:
            d["reply_to"] = self.reply_to
        if self.cc is not None:
            d["cc"] = self.cc
        if self.bcc is not None:
            d["bcc"] = self.bcc
        if self.tags is not None:
            d["tags"] = self.tags
        if self.scheduled_at is not None:
            d["scheduled_at"] = self.scheduled_at
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
    from_name: str | None = None
    reply_to: str | None = None
    sent_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Email:
        data = unwrap(data)
        return cls(
            id=data["id"],
            from_=data["from"],
            to=data["to"],
            subject=data["subject"],
            status=data["status"],
            created_at=data.get("created_at", data.get("createdAt", "")),
            html=data.get("html"),
            text=data.get("text"),
            from_name=data.get("from_name"),
            reply_to=data.get("reply_to"),
            sent_at=data.get("sent_at"),
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
        data = unwrap(data)
        return cls(
            id=data["id"],
            name=data["name"],
            status=data.get("status", "pending"),
            records=data.get("records", data.get("dns_records", [])),
            created_at=data.get("created_at", data.get("createdAt", "")),
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
        data = unwrap(data)
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            permission=data.get("permission", data.get("key_permission", "")),
            created_at=data.get("created_at", data.get("createdAt", "")),
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
        data = unwrap(data)
        return cls(
            id=data["id"],
            url=data.get("url", ""),
            events=data.get("events", []),
            created_at=data.get("created_at", data.get("createdAt", "")),
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
        data = unwrap(data)
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            created_at=data.get("created_at", data.get("createdAt", "")),
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
    total: int = 0
    by_status: dict[str, int] = field(default_factory=dict)
    delivery_rate: float = 0.0
    bounce_rate: float = 0.0
    complaint_rate: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Metrics:
        data = unwrap(data)
        ts = [
            MetricsDataPoint(**point) for point in data.get("timeseries", [])
        ]
        return cls(
            sent=data.get("sent", 0),
            delivered=data.get("delivered", 0),
            opened=data.get("opened", 0),
            clicked=data.get("clicked", 0),
            bounced=data.get("bounced", 0),
            complained=data.get("complained", 0),
            timeseries=ts,
            total=data.get("total", 0),
            by_status=data.get("by_status", {}),
            delivery_rate=data.get("delivery_rate", 0.0),
            bounce_rate=data.get("bounce_rate", 0.0),
            complaint_rate=data.get("complaint_rate", 0.0),
        )
