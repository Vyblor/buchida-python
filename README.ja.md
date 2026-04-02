<div align="center">
  <img src="assets/logo-black.svg" alt="buchida" width="280" />
  <p><strong>CJKサポートを備えた開発者向けメールAPI</strong></p>

  [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [中文](README.zh.md)

  [![PyPI version](https://img.shields.io/pypi/v/buchida)](https://pypi.org/project/buchida/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

[buchida](https://buchida.com)メールAPIの公式Python SDKです。

## インストール

```bash
pip install buchida
```

```bash
poetry add buchida
```

## クイックスタート

```python
from buchida import Buchida

client = Buchida("bc_live_xxxxxxxxxxxxxxxxxxxxx")

result = client.emails.send(
    from_="hello@yourdomain.com",
    to="user@example.com",
    subject="buchidaへようこそ！",
    html="<h1>こんにちは！</h1><p>ご登録ありがとうございます。</p>",
)

print(f"メール送信完了: {result['id']}")
```

## 特徴

- 完全な型ヒントサポート
- 依存関係ゼロ（標準ライブラリ`urllib`）
- Python 3.10+
- 型付きdataclassレスポンス

## ドキュメント

- [クイックスタート](https://buchida.com/ja/docs/quickstart)
- [APIリファレンス](https://buchida.com/ja/docs/sending-email)
- [GitHub](https://github.com/Vyblor/buchida-python)

## ライセンス

MIT
