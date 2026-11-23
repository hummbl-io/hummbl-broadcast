# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately:

1. **Do not open a public GitHub issue.**
2. Go to [Security Advisories](https://github.com/hummbl-io/hummbl-broadcast/security/advisories/new) and create a private security advisory, or email `security@hummbl.io`.
3. Include a description of the vulnerability, steps to reproduce, and potential impact.

We aim to respond within 48 hours and coordinate a responsible disclosure timeline.

## Scope

This policy covers the code in this repository only. For vulnerabilities in
dependencies, report them to the upstream maintainer. The RTMP stream key is
never passed in a child process argument list; see `src/hummbl_broadcast/publisher.py`
and `tests/test_publisher_security.py` for the property that enforces it.

## Standard

This repository adheres to the HUMMBL Organization Security Standards. The
canonical fleet rules live in the shared governance corpus (`~/.agents/rules/`
on fleet hosts). `hummbl-io/hummbl-governance` is archived and retained for
history only.

Automated dependency updates are configured in `.github/dependabot.yml`, and
GitHub secret scanning is enabled for this repository.
