from __future__ import annotations

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Any

from buchida.errors import (
    AuthenticationError,
    BuchidaError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from buchida.types import (
    ApiKey,
    Domain,
    Email,
    Metrics,
    SendEmailParams,
    Template,
    Webhook,
    BatchResponse,
    ListResponse,
    SendResult,
    unwrap,
)

DEFAULT_BASE_URL = "https://api.buchida.com/v1"
DEFAULT_TIMEOUT = 30


class Buchida:
    """buchida email API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if not api_key:
            raise ValueError("API key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        self.emails = _Emails(self)
        self.domains = _Domains(self)
        self.api_keys = _ApiKeys(self)
        self.webhooks = _Webhooks(self)
        self.templates = _Templates(self)
        self.metrics = _Metrics(self)

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None

        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "User-Agent": "buchida-python/0.2.1",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                if resp.status == 204:
                    return None
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read().decode("utf-8"))
                err = error_body.get("error")
                if isinstance(err, dict):
                    message = err.get("message", e.reason)
                else:
                    message = error_body.get("message", e.reason)
            except Exception:
                message = e.reason
            raise self._make_error(e.code, message) from None

    @staticmethod
    def _make_error(status: int, message: str) -> BuchidaError:
        match status:
            case 401:
                return AuthenticationError(message)
            case 404:
                return NotFoundError(message)
            case 422:
                return ValidationError(message)
            case 429:
                return RateLimitError(message)
            case _:
                return BuchidaError(message, status)


class _Emails:
    def __init__(self, client: Buchida):
        self._client = client

    def send(
        self,
        *,
        from_: str,
        to: str | list[str],
        subject: str,
        html: str | None = None,
        text: str | None = None,
        reply_to: str | None = None,
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        tags: dict[str, str] | None = None,
        scheduled_at: str | None = None,
        from_name: str | None = None,
    ) -> SendResult:
        params = SendEmailParams(
            from_=from_,
            to=to,
            subject=subject,
            html=html,
            text=text,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            tags=tags,
            scheduled_at=scheduled_at,
            from_name=from_name,
        )
        resp = self._client._request("POST", "/emails", params.to_dict())
        return SendResult(unwrap(resp) or {})

    def get(self, email_id: str) -> Email:
        data = self._client._request("GET", f"/emails/{email_id}")
        return Email.from_dict(data)

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        direction: str | None = None,
    ) -> ListResponse:
        """List emails.

        ``from_`` / ``to`` filter by sender / recipient *address* (not dates).
        ``from_date`` / ``to_date`` (ISO 8601) filter by creation date;
        ``direction`` is ``"inbound"`` or ``"outbound"``.
        """
        params: dict[str, str] = {}
        if cursor:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = str(limit)
        if status:
            params["status"] = status
        if from_:
            params["from"] = from_
        if to:
            params["to"] = to
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        if direction:
            params["direction"] = direction
        qs = urllib.parse.urlencode(params)
        path = f"/emails?{qs}" if qs else "/emails"
        return ListResponse.from_envelope(self._client._request("GET", path))

    def cancel(self, email_id: str) -> None:
        self._client._request("POST", f"/emails/{email_id}/cancel")

    def send_batch(self, emails: list[dict[str, Any]]) -> BatchResponse:
        """Send up to 100 emails; returns one ``{"data": ...}`` / ``{"error": ...}`` per input."""
        return BatchResponse.from_envelope(
            self._client._request("POST", "/emails/batch", emails)
        )


class _Domains:
    def __init__(self, client: Buchida):
        self._client = client

    def create(self, *, name: str) -> Domain:
        resp = self._client._request("POST", "/domains", {"name": name})
        return Domain.from_dict(resp)

    def list(self) -> list[Domain]:
        resp = self._client._request("GET", "/domains")
        items = unwrap(resp)
        return [Domain.from_dict(d) for d in items]

    def get(self, domain_id: str) -> Domain:
        data = self._client._request("GET", f"/domains/{domain_id}")
        return Domain.from_dict(data)

    def verify(self, domain_id: str) -> Domain:
        data = self._client._request("POST", f"/domains/{domain_id}/verify")
        return Domain.from_dict(data)


class _ApiKeys:
    def __init__(self, client: Buchida):
        self._client = client

    def create(self, *, name: str, permission: str) -> ApiKey:
        data = self._client._request(
            "POST", "/api-keys", {"name": name, "permission": permission}
        )
        return ApiKey.from_dict(data)

    def list(self) -> list[ApiKey]:
        resp = self._client._request("GET", "/api-keys")
        items = unwrap(resp)
        return [ApiKey.from_dict(d) for d in items]

    def delete(self, key_id: str) -> None:
        self._client._request("DELETE", f"/api-keys/{key_id}")


class _Webhooks:
    def __init__(self, client: Buchida):
        self._client = client

    def create(self, *, url: str, events: list[str]) -> Webhook:
        data = self._client._request(
            "POST", "/webhooks", {"url": url, "events": events}
        )
        return Webhook.from_dict(data)

    def list(self) -> list[Webhook]:
        resp = self._client._request("GET", "/webhooks")
        items = unwrap(resp)
        return [Webhook.from_dict(d) for d in items]

    def delete(self, webhook_id: str) -> None:
        self._client._request("DELETE", f"/webhooks/{webhook_id}")


class _Templates:
    def __init__(self, client: Buchida):
        self._client = client

    def list(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
    ) -> list[Template]:
        """List templates. ``status`` is ``"draft"`` or ``"published"``; ``search`` matches name/subject."""
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        qs = urllib.parse.urlencode(params)
        resp = self._client._request("GET", f"/templates?{qs}" if qs else "/templates")
        items = unwrap(resp)
        return [Template.from_dict(d) for d in items]

    def get(self, template_id: str) -> Template:
        data = self._client._request("GET", f"/templates/{template_id}")
        return Template.from_dict(data)


class _Metrics:
    def __init__(self, client: Buchida):
        self._client = client

    def get(
        self,
        *,
        from_: str,
        to: str,
        granularity: str | None = None,
    ) -> Metrics:
        # The API filters on from_date/to_date; plain from/to were silently ignored.
        params: dict[str, str] = {"from_date": from_, "to_date": to}
        if granularity:
            params["granularity"] = granularity
        qs = urllib.parse.urlencode(params)
        data = self._client._request("GET", f"/metrics?{qs}")
        return Metrics.from_dict(data)
