# Validation boundary — 2026-10-28

Observed locally on Linux with Node 26.11.1, Python 3 and Codex CLI 0.163.0:

- 19 suite packaging/installer tests: deterministic individual/full bytes, no-overwrite dry run, user edits, exact marketplace/artifact inventory, path traversal, symlink/dangling-link/hardlink protection and unknown-directory preservation and other standalone discovery-scope collisions. The final regression verifies root marketplace receipt symlinks are rejected before receipt reads.
- 9 canonical skills also passed the installed skill-creator frontmatter validator.
- 14 retained Spec/History CLI tests: original structural evidence semantics and history manual-content/event-identity protection, run with a synthetic temporary directory inside this repository.
- 16 synthetic maturity checks: generic profiles load, Decimal rounding, independent business value, malformed totals/weights/missing evidence, scale drift and item-change attribution guards, generic-only profile boundaries, portable evidence locators and explicitly synthetic benchmark calculations.
- Native repository-root local marketplace (generated packages checked in): history-only plugin and full suite installed separately, listed by Codex, all package bytes read back and compared, then removed. Isolated `CODEX_HOME`, no credentials or model calls.

Reproduce suite checks with `node --test tests/*.test.mjs`; calculators with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/aes-maturity/tests`; native checks with `node scripts/native-smoke.mjs` after build. Native smoke requires the host's Codex CLI and is not part of ordinary skill use.

The installer assumes a single writer and trusted local receipts. It does not guarantee atomic multi-module rollback after I/O failure. Custom/remote host caches and another skill-discovery scope need separate collision review. Native installation does not prove model execution, cross-platform compatibility, public-directory approval or semantic product acceptance. No real financial data or provider tests were used.
