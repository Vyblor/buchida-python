<div align="center">
  <img src="assets/logo-black.svg" alt="buchida" width="280" />
  <p><strong>buchida Python SDK — Email API for AI agents</strong></p>

  [**English**](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [中文](README.zh.md)

  [![PyPI version](https://img.shields.io/pypi/v/buchida)](https://pypi.org/project/buchida) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

buchida is the official Python SDK for **buchida** — an email API built for AI agents. buchida ships a CLI, an MCP server, and SDKs in 5 languages (Node, Python, Go, Ruby, Java), all sharing the same REST API surface. `@buchida/email` templates render Korean, Japanese, and Chinese natively.

## Install

```bash
pip install buchida
```

## Send your first email

```python
import os

from buchida import Buchida

client = Buchida(os.environ["BUCHIDA_API_KEY"])

result = client.emails.send(
    from_="hello@yourapp.com",
    from_name="Your App",
    to="user@example.com",
    subject="Hello",
    html="<h1>Welcome</h1>",
)
print(result["id"], result["status"])  # unwrapped payload

# Lists are plain lists with .cursor / .has_more
page = client.emails.list(limit=20)
for item in page:
    print(item["id"], item["status"])
if page.has_more:
    next_page = client.emails.list(cursor=page.cursor)

# Batch: one result per input, each with .data or .error
for r in client.emails.send_batch([
    {"from": "hello@yourapp.com", "to": "a@example.com", "subject": "A", "text": "hi"},
]):
    print(r.data if r.ok else r.error)

# Typed models (snake_case fields)
email = client.emails.get(result["id"])
print(email.from_name, email.created_at)
```

## Upgrading to 0.2

- The API wraps responses in `{"data": ...}`; the SDK now returns the unwrapped payload.
  `emails.send()` returns the email object (`result["id"]`), `emails.list()` returns a list
  with `.cursor` and `.has_more`, and `emails.send_batch()` returns a list of results that
  each have `.data` or `.error`.
- Backwards compatible: `result["data"]` (send) and `page["data"]`, `page["cursor"]`,
  `page["hasMore"]` (list) still work (no warning is emitted; they are deprecated in docs only), as do
  `"data" in res`, `res.get("cursor")` and `res.keys()`. Migrate to the unwrapped form; the shim
  will be removed in a future major version. Caveats: list results are now `list` subclasses, so
  `isinstance(res, dict)` is `False` and an empty page is falsy (`if not res`).
- `emails.get`, `domains.get/verify`, `api_keys.create`, `webhooks.create`, `templates.get`
  and `metrics.get` previously raised `KeyError` (they parsed the envelope instead of the
  payload); they now return populated models. Model date fields (`created_at`, ...) were
  read from camelCase keys and are now read from the API's snake_case keys.
- New: `from_name` on `emails.send()` and the `Email` model; request bodies use snake_case
  (`reply_to`, `scheduled_at`); API errors with a nested `{"error": {"message": ...}}` body
  are surfaced correctly.

## Documentation

Full docs: **[buchida.com/docs](https://buchida.com/docs)**

- API reference: https://buchida.com/docs/api-reference
- Quickstart guide: https://buchida.com/docs/quickstart
- CJK email templates: https://buchida.com/docs/templates
- MCP server setup: https://buchida.com/docs/mcp
- CLI reference: https://buchida.com/docs/cli

## Links

- **Website:** [buchida.com](https://buchida.com)
- **Documentation:** [buchida.com/docs](https://buchida.com/docs)
- **Pricing:** [buchida.com/pricing](https://buchida.com/pricing)
- **GitHub:** https://github.com/Vyblor/buchida-python

## License

MIT
