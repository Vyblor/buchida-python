<div align="center">
  <img src="assets/logo-black.svg" alt="buchida" width="280" />
  <p><strong>buchida Python SDK — AI エージェントのためのメール API</strong></p>

  [English](README.md) | [한국어](README.ko.md) | [**日本語**](README.ja.md) | [中文](README.zh.md)

  [![PyPI version](https://img.shields.io/pypi/v/buchida)](https://pypi.org/project/buchida) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

buchida は AI エージェントのために作られたメール API の公式 Python SDK です。buchida は CLI、MCP サーバー、そして 5 言語の SDK (Node、Python、Go、Ruby、Java) を提供しており、すべて同じ REST API 表面を共有しています。`@buchida/email` テンプレートは韓国語、日本語、中国語をネイティブにレンダリングします。

## インストール

```bash
pip install buchida
```

## 最初のメールを送信

```python
import buchida

client = buchida.Client(api_key=os.environ["BUCHIDA_API_KEY"])

client.emails.send(
    from_="hello@yourapp.com",
    to="user@example.com",
    subject="こんにちは",
    html="<h1>ようこそ</h1>",
)
```

## ドキュメント

完全なドキュメント: **[buchida.com/docs](https://buchida.com/docs)**

- API リファレンス: https://buchida.com/docs/api-reference
- クイックスタートガイド: https://buchida.com/docs/quickstart
- CJK メールテンプレート: https://buchida.com/docs/templates
- MCP サーバーセットアップ: https://buchida.com/docs/mcp
- CLI リファレンス: https://buchida.com/docs/cli

## リンク

- **ウェブサイト:** [buchida.com](https://buchida.com)
- **ドキュメント:** [buchida.com/docs](https://buchida.com/docs)
- **料金:** [buchida.com/pricing](https://buchida.com/pricing)
- **GitHub:** https://github.com/Vyblor/buchida-python

## ライセンス

MIT
