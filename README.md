# buchida

Official Python SDK for the [buchida](https://buchida.com) email API.

## Installation

```bash
pip install buchida
```

## Quick Start

```python
from buchida import Buchida

client = Buchida("bc_live_xxxxxxxxxxxxxxxxxxxxx")

# Send an email
result = client.emails.send(
    from_="hello@yourdomain.com",
    to="user@example.com",
    subject="Welcome to buchida!",
    html="<h1>Hello!</h1><p>Welcome aboard.</p>",
)

print(f"Email sent: {result['id']}")
```

## Features

- Full type hints
- Zero dependencies (stdlib `urllib`)
- Python 3.10+
- Typed dataclass responses

## API Reference

### Emails

```python
client.emails.send(from_="...", to="...", subject="...", html="...", text="...")
client.emails.send_batch([{"from": "...", "to": "...", "subject": "..."}])
client.emails.get("email_id")
client.emails.list(limit=10, status="delivered")
client.emails.cancel("email_id")
```

### Domains

```python
client.domains.create(name="yourdomain.com")
client.domains.list()
client.domains.get("domain_id")
client.domains.verify("domain_id")
```

### API Keys

```python
client.api_keys.create(name="Production", permission="full_access")
client.api_keys.list()
client.api_keys.delete("key_id")
```

### Webhooks

```python
client.webhooks.create(url="https://example.com/webhook", events=["email.delivered"])
client.webhooks.list()
client.webhooks.delete("webhook_id")
```

### Templates

```python
client.templates.list()
client.templates.get("template_id")
```

### Metrics

```python
client.metrics.get(from_="2026-03-01", to="2026-03-31", granularity="day")
```

## Error Handling

```python
from buchida import Buchida, AuthenticationError, RateLimitError, BuchidaError

try:
    client.emails.send(...)
except AuthenticationError:
    # 401 - invalid API key
    pass
except RateLimitError:
    # 429 - too many requests
    pass
except BuchidaError as e:
    # Other API errors
    print(e.status_code, e.message)
```

## License

MIT
