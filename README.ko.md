<div align="center">
  <img src="assets/logo-black.svg" alt="buchida" width="280" />
  <p><strong>CJK 지원을 갖춘 개발자 중심 이메일 API</strong></p>

  [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [中文](README.zh.md)

  [![PyPI version](https://img.shields.io/pypi/v/buchida)](https://pypi.org/project/buchida/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

[buchida](https://buchida.com) 이메일 API의 공식 Python SDK입니다.

## 설치

```bash
pip install buchida
```

```bash
poetry add buchida
```

## 빠른 시작

```python
from buchida import Buchida

client = Buchida("bc_live_xxxxxxxxxxxxxxxxxxxxx")

result = client.emails.send(
    from_="hello@yourdomain.com",
    to="user@example.com",
    subject="buchida에 오신 것을 환영합니다!",
    html="<h1>안녕하세요!</h1><p>가입을 환영합니다.</p>",
)

print(f"이메일 발송 완료: {result['id']}")
```

## 주요 기능

- 완전한 타입 힌트 지원
- 의존성 없음 (표준 라이브러리 `urllib`)
- Python 3.10+
- 타입이 지정된 dataclass 응답

## 문서

- [빠른 시작 가이드](https://buchida.com/ko/docs/quickstart)
- [API 레퍼런스](https://buchida.com/ko/docs/sending-email)
- [GitHub](https://github.com/Vyblor/buchida-python)

## 라이선스

MIT
