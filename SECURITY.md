# Security Policy

We take the security of InvenXis seriously. Thanks for helping us keep the project
and its users safe.

## Reporting a Vulnerability

**Please do not open a public issue for security problems.** Instead, report the issue
privately by opening a [security advisory][advisories] on GitHub.

You should receive an acknowledgement within 48 hours. Once we triage the report, you
can expect:

1. A confirmation that the report was received.
2. A timeline for a fix and release, depending on severity.
3. Credit in the advisory if you would like to be acknowledged.

## Supported Versions

| Version  | Supported          |
|----------|--------------------|
| 1.1.x    | :white_check_mark: |

## Security Notes

- Secrets are loaded from environment variables (`.env`), never hardcoded.
- Production Django settings enable HTTPS redirect, HSTS, secure cookies, and
  `DEBUG=False` guards via a hardened settings block.
- JWT access tokens are short-lived with refresh-rotation enabled.

[advisories]: https://github.com/Zultes-Dev/InvenXis/security/advisories