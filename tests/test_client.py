import json
import warnings
import urllib.error
import urllib.request
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from buchida import (
    AuthenticationError,
    Buchida,
    BuchidaError,
    RateLimitError,
    ValidationError,
)


def _mock_response(status: int, body: dict | list | None = None):
    """Create a mock urllib response."""
    data = json.dumps(body).encode("utf-8") if body is not None else b""
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = data
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _mock_http_error(status: int, body: dict | None = None):
    """Create a mock HTTPError."""
    data = json.dumps(body).encode("utf-8") if body else b'{"message":"error"}'
    error = urllib.error.HTTPError(
        url="https://api.buchida.com/test",
        code=status,
        msg="Error",
        hdrs=None,  # type: ignore
        fp=BytesIO(data),
    )
    return error


class TestBuchidaInit:
    def test_requires_api_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            Buchida("")

    def test_accepts_options(self):
        client = Buchida(
            "bc_test_xxx",
            base_url="https://custom.api.com",
            timeout=60,
        )
        assert client._base_url == "https://custom.api.com"
        assert client._timeout == 60


class TestEmails:
    @patch("urllib.request.urlopen")
    def test_send(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            200, {"data": {"id": "email_123", "status": "queued"}}
        )
        client = Buchida("bc_test_xxx")
        result = client.emails.send(
            from_="hi@buchida.com",
            to="user@example.com",
            subject="Hello",
            html="<p>Hi</p>",
        )
        assert result["id"] == "email_123"
        assert result["status"] == "queued"

    @patch("urllib.request.urlopen")
    def test_get(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "id": "email_123",
            "from": "hi@buchida.com",
            "from_name": "Vyblor",
            "to": ["user@example.com"],
            "subject": "Hello",
            "status": "delivered",
            "reply_to": "support@buchida.com",
            "created_at": "2026-03-31T00:00:00Z",
            "sent_at": "2026-03-31T00:00:05Z",
        }})
        client = Buchida("bc_test_xxx")
        email = client.emails.get("email_123")
        assert email.id == "email_123"
        assert email.status == "delivered"
        assert email.from_name == "Vyblor"
        assert email.reply_to == "support@buchida.com"
        assert email.created_at == "2026-03-31T00:00:00Z"
        assert email.sent_at == "2026-03-31T00:00:05Z"

    @patch("urllib.request.urlopen")
    def test_list(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            200, {"data": [{"id": "e1"}, {"id": "e2"}], "cursor": "c2", "hasMore": True}
        )
        client = Buchida("bc_test_xxx")
        result = client.emails.list(limit=10, status="delivered")
        assert [e["id"] for e in result] == ["e1", "e2"]
        assert result.cursor == "c2"
        assert result.has_more is True
        assert result.data is result

    @patch("urllib.request.urlopen")
    def test_list_legacy_envelope_access(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            200, {"data": [{"id": "e1"}], "cursor": "c2", "hasMore": True}
        )
        client = Buchida("bc_test_xxx")
        result = client.emails.list()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert result["data"][0]["id"] == "e1"
            assert result["cursor"] == "c2"
            assert result["hasMore"] is True
            assert result.get("cursor") == "c2"
            assert result.get("hasMore") is True
            assert result.get("missing", "d") == "d"
            assert "hasMore" in result and "cursor" in result and "data" in result
            assert result.keys() == ["data", "cursor", "hasMore"]
            assert result[0]["id"] == "e1"
            assert json.dumps(result) == '[{"id": "e1"}]'

    @patch("urllib.request.urlopen")
    def test_send_legacy_data_access(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {"id": "email_123"}})
        client = Buchida("bc_test_xxx")
        result = client.emails.send(from_="a@b.com", to="c@d.com", subject="s", text="t")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert result["data"]["id"] == "email_123"
            assert result.get("data") is result
            assert "data" in result
            assert "id" in result
        # No self-reference is stored, so the result stays JSON serialisable.
        assert json.dumps(result) == '{"id": "email_123"}'

    @patch("urllib.request.urlopen")
    def test_batch_legacy_data_access(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": [{"data": {"id": "e1"}}]})
        client = Buchida("bc_test_xxx")
        result = client.emails.send_batch([{"from": "a@b.com", "to": "c@d.com", "subject": "s"}])
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert result["data"][0].data["id"] == "e1"
            assert result.get("data") is result
            assert "data" in result
            assert result.get("cursor") is None

    @patch("urllib.request.urlopen")
    def test_cancel(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(204)
        client = Buchida("bc_test_xxx")
        client.emails.cancel("email_123")
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_send_batch(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": [
            {"data": {"id": "email_1", "status": "queued"}},
            {"error": {"code": "invalid_email_address", "message": "bad to"}},
        ]})
        client = Buchida("bc_test_xxx")
        result = client.emails.send_batch([
            {"from": "hi@buchida.com", "to": "a@example.com", "subject": "A"},
            {"from": "hi@buchida.com", "to": "b@example.com", "subject": "B"},
        ])
        assert len(result) == 2
        assert result[0].data["id"] == "email_1"
        assert result[0].ok and result[0].error is None
        assert not result[1].ok
        assert result[1].error["code"] == "invalid_email_address"
        assert result[1]["error"]["message"] == "bad to"


class TestDomains:
    @patch("urllib.request.urlopen")
    def test_create(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "id": "dom_1",
            "name": "example.com",
            "status": "pending",
            "dns_records": [{"type": "TXT"}],
            "created_at": "2026-03-31T00:00:00Z",
        }})
        client = Buchida("bc_test_xxx")
        domain = client.domains.create(name="example.com")
        assert domain.name == "example.com"
        assert domain.created_at == "2026-03-31T00:00:00Z"
        assert domain.records == [{"type": "TXT"}]

    @patch("urllib.request.urlopen")
    def test_list(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": []})
        client = Buchida("bc_test_xxx")
        domains = client.domains.list()
        assert isinstance(domains, list)

    @patch("urllib.request.urlopen")
    def test_verify(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "id": "dom_1",
            "name": "example.com",
            "status": "verified",
            "dns_records": [{"type": "TXT"}],
            "created_at": "2026-03-31T00:00:00Z",
        }})
        client = Buchida("bc_test_xxx")
        domain = client.domains.verify("dom_1")
        assert domain.status == "verified"


class TestApiKeys:
    @patch("urllib.request.urlopen")
    def test_create(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "id": "key_1",
            "name": "test",
            "key": "bc_live_newkey",
            "permission": "full_access",
            "created_at": "2026-03-31T00:00:00Z",
        }})
        client = Buchida("bc_test_xxx")
        key = client.api_keys.create(name="test", permission="full_access")
        assert key.key == "bc_live_newkey"
        assert key.created_at == "2026-03-31T00:00:00Z"

    @patch("urllib.request.urlopen")
    def test_delete(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(204)
        client = Buchida("bc_test_xxx")
        client.api_keys.delete("key_1")
        mock_urlopen.assert_called_once()


class TestWebhooks:
    @patch("urllib.request.urlopen")
    def test_create(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "id": "wh_1",
            "url": "https://example.com/wh",
            "events": ["email.delivered"],
            "created_at": "2026-03-31T00:00:00Z",
        }})
        client = Buchida("bc_test_xxx")
        wh = client.webhooks.create(url="https://example.com/wh", events=["email.delivered"])
        assert wh.id == "wh_1"
        assert wh.created_at == "2026-03-31T00:00:00Z"


class TestTemplates:
    @patch("urllib.request.urlopen")
    def test_list(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, [])
        client = Buchida("bc_test_xxx")
        result = client.templates.list()
        assert isinstance(result, list)

    @patch("urllib.request.urlopen")
    def test_get(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "id": "tpl_1",
            "name": "Welcome",
            "created_at": "2026-03-31T00:00:00Z",
        }})
        client = Buchida("bc_test_xxx")
        tpl = client.templates.get("tpl_1")
        assert tpl.name == "Welcome"
        assert tpl.created_at == "2026-03-31T00:00:00Z"


class TestMetrics:
    @patch("urllib.request.urlopen")
    def test_get(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "sent": 100,
            "delivered": 95,
            "opened": 50,
            "clicked": 10,
            "bounced": 3,
            "complained": 1,
            "timeseries": [],
        }})
        client = Buchida("bc_test_xxx")
        metrics = client.metrics.get(from_="2026-03-01", to="2026-03-31", granularity="day")
        assert metrics.sent == 100
        url = mock_urlopen.call_args[0][0].full_url
        assert "from_date=2026-03-01" in url and "to_date=2026-03-31" in url


class TestSendWireFormat:
    @patch("urllib.request.urlopen")
    def test_send_uses_snake_case_keys(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {"id": "email_123"}})
        client = Buchida("bc_test_xxx")
        client.emails.send(
            from_="hi@buchida.com",
            from_name="Vyblor",
            to="user@example.com",
            subject="Hello",
            html="<p>Hi</p>",
            reply_to="support@buchida.com",
            scheduled_at="2026-12-01T00:00:00Z",
        )
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        assert body["from_name"] == "Vyblor"
        assert body["reply_to"] == "support@buchida.com"
        assert body["scheduled_at"] == "2026-12-01T00:00:00Z"
        assert "replyTo" not in body
        assert "scheduledAt" not in body


class TestErrorHandling:
    @patch("urllib.request.urlopen")
    def test_nested_error_message(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_http_error(
            422, {"error": {"code": "validation_error", "message": "from_name is invalid"}}
        )
        client = Buchida("bc_test_xxx")
        with pytest.raises(ValidationError, match="from_name is invalid"):
            client.emails.list()

    @patch("urllib.request.urlopen")
    def test_legacy_error_message(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_http_error(422, {"message": "legacy msg"})
        client = Buchida("bc_test_xxx")
        with pytest.raises(ValidationError, match="legacy msg"):
            client.emails.list()

    @patch("urllib.request.urlopen")
    def test_401_raises_authentication_error(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_http_error(401, {"message": "Invalid API key"})
        client = Buchida("bc_test_bad")
        with pytest.raises(AuthenticationError):
            client.emails.list()

    @patch("urllib.request.urlopen")
    def test_429_raises_rate_limit_error(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_http_error(429, {"message": "Rate limit exceeded"})
        client = Buchida("bc_test_xxx")
        with pytest.raises(RateLimitError):
            client.emails.list()

    @patch("urllib.request.urlopen")
    def test_500_raises_buchida_error(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_http_error(500, {"message": "Internal server error"})
        client = Buchida("bc_test_xxx")
        with pytest.raises(BuchidaError):
            client.emails.list()


class TestCustomBaseUrl:
    @patch("urllib.request.urlopen")
    def test_custom_base_url(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, [])
        client = Buchida("bc_test_xxx", base_url="https://custom.api.com")
        client.domains.list()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.full_url.startswith("https://custom.api.com")


class TestMetricsCurrentShape:
    @patch("urllib.request.urlopen")
    def test_get_current_api_shape(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": {
            "total": 10, "by_status": {"delivered": 9}, "delivery_rate": 0.9,
        }})
        client = Buchida("bc_test_xxx")
        m = client.metrics.get(from_="2026-03-01", to="2026-03-31")
        assert m.total == 10
        assert m.by_status == {"delivered": 9}
        assert m.delivery_rate == 0.9
