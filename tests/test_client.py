import json
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
        mock_urlopen.return_value = _mock_response(200, {"id": "email_123"})
        client = Buchida("bc_test_xxx")
        result = client.emails.send(
            from_="hi@buchida.com",
            to="user@example.com",
            subject="Hello",
            html="<p>Hi</p>",
        )
        assert result["id"] == "email_123"

    @patch("urllib.request.urlopen")
    def test_get(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "id": "email_123",
            "from": "hi@buchida.com",
            "to": ["user@example.com"],
            "subject": "Hello",
            "status": "delivered",
            "createdAt": "2026-03-31T00:00:00Z",
        })
        client = Buchida("bc_test_xxx")
        email = client.emails.get("email_123")
        assert email.id == "email_123"
        assert email.status == "delivered"

    @patch("urllib.request.urlopen")
    def test_list(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {"data": [], "cursor": None})
        client = Buchida("bc_test_xxx")
        result = client.emails.list(limit=10, status="delivered")
        assert "data" in result

    @patch("urllib.request.urlopen")
    def test_cancel(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(204)
        client = Buchida("bc_test_xxx")
        client.emails.cancel("email_123")
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_send_batch(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, [
            {"id": "email_1"},
            {"id": "email_2"},
        ])
        client = Buchida("bc_test_xxx")
        result = client.emails.send_batch([
            {"from": "hi@buchida.com", "to": "a@example.com", "subject": "A"},
            {"from": "hi@buchida.com", "to": "b@example.com", "subject": "B"},
        ])
        assert len(result) == 2


class TestDomains:
    @patch("urllib.request.urlopen")
    def test_create(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "id": "dom_1",
            "name": "example.com",
            "status": "pending",
            "records": [],
            "createdAt": "2026-03-31T00:00:00Z",
        })
        client = Buchida("bc_test_xxx")
        domain = client.domains.create(name="example.com")
        assert domain.name == "example.com"

    @patch("urllib.request.urlopen")
    def test_list(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, [])
        client = Buchida("bc_test_xxx")
        domains = client.domains.list()
        assert isinstance(domains, list)

    @patch("urllib.request.urlopen")
    def test_verify(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "id": "dom_1",
            "name": "example.com",
            "status": "verified",
            "records": [],
            "createdAt": "2026-03-31T00:00:00Z",
        })
        client = Buchida("bc_test_xxx")
        domain = client.domains.verify("dom_1")
        assert domain.status == "verified"


class TestApiKeys:
    @patch("urllib.request.urlopen")
    def test_create(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "id": "key_1",
            "name": "test",
            "key": "bc_live_newkey",
            "permission": "full_access",
            "createdAt": "2026-03-31T00:00:00Z",
        })
        client = Buchida("bc_test_xxx")
        key = client.api_keys.create(name="test", permission="full_access")
        assert key.key == "bc_live_newkey"

    @patch("urllib.request.urlopen")
    def test_delete(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(204)
        client = Buchida("bc_test_xxx")
        client.api_keys.delete("key_1")
        mock_urlopen.assert_called_once()


class TestWebhooks:
    @patch("urllib.request.urlopen")
    def test_create(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "id": "wh_1",
            "url": "https://example.com/wh",
            "events": ["email.delivered"],
            "createdAt": "2026-03-31T00:00:00Z",
        })
        client = Buchida("bc_test_xxx")
        wh = client.webhooks.create(url="https://example.com/wh", events=["email.delivered"])
        assert wh.id == "wh_1"


class TestTemplates:
    @patch("urllib.request.urlopen")
    def test_list(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, [])
        client = Buchida("bc_test_xxx")
        result = client.templates.list()
        assert isinstance(result, list)

    @patch("urllib.request.urlopen")
    def test_get(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "id": "tpl_1",
            "name": "Welcome",
            "createdAt": "2026-03-31T00:00:00Z",
        })
        client = Buchida("bc_test_xxx")
        tpl = client.templates.get("tpl_1")
        assert tpl.name == "Welcome"


class TestMetrics:
    @patch("urllib.request.urlopen")
    def test_get(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, {
            "sent": 100,
            "delivered": 95,
            "opened": 50,
            "clicked": 10,
            "bounced": 3,
            "complained": 1,
            "timeseries": [],
        })
        client = Buchida("bc_test_xxx")
        metrics = client.metrics.get(from_="2026-03-01", to="2026-03-31", granularity="day")
        assert metrics.sent == 100


class TestErrorHandling:
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
