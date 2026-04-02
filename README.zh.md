<div align="center">
  <img src="assets/logo-black.svg" alt="buchida" width="280" />
  <p><strong>支持CJK的开发者优先邮件API</strong></p>

  [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [中文](README.zh.md)

  [![PyPI version](https://img.shields.io/pypi/v/buchida)](https://pypi.org/project/buchida/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

[buchida](https://buchida.com)邮件API的官方Python SDK。

## 安装

```bash
pip install buchida
```

```bash
poetry add buchida
```

## 快速开始

```python
from buchida import Buchida

client = Buchida("bc_live_xxxxxxxxxxxxxxxxxxxxx")

result = client.emails.send(
    from_="hello@yourdomain.com",
    to="user@example.com",
    subject="欢迎使用buchida！",
    html="<h1>你好！</h1><p>欢迎加入。</p>",
)

print(f"邮件发送成功: {result['id']}")
```

## 特性

- 完整的类型提示
- 零依赖（标准库`urllib`）
- Python 3.10+
- 类型化dataclass响应

## 文档

- [快速开始](https://buchida.com/zh/docs/quickstart)
- [API参考](https://buchida.com/zh/docs/sending-email)
- [GitHub](https://github.com/Vyblor/buchida-python)

## 许可证

MIT
