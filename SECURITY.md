# Security Policy

## Supported versions

Security fixes are applied on the `main` branch of this repository.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive reports.

Email the maintainer at **jayaramhnambiar@gmail.com** with:

- A description of the issue
- Steps to reproduce (or a proof of concept)
- Impact assessment if known

You should receive an acknowledgement within a reasonable time. Please allow
time for investigation before any public disclosure.

## Scope notes

- This project does **not** require API keys for its default geocoding path.
- Do not commit `.env` files, tokens, or private keys. See `.gitignore`.
- Public demo deployments (for example on Render free tier) are shared
  infrastructure; treat them as untrusted for sensitive workloads and expect
  fair-use limits from upstream geocoders.
