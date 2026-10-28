# Installation

Published source includes generated packages. Rebuild after source changes with `node scripts/build.mjs`. Each `dist/standalone/<module>` contains only that skill; `dist/standalone/all` contains the suite. Each `dist/plugins/<module>` is one plugin; `dist/plugins/all` is the suite plugin. These are generated from identical source bytes.

## Standalone

Choose an explicit target skill directory. The command below is a dry run and makes no changes:

```sh
node scripts/install-skills.mjs --module history --target /path/to/project/.agents/skills
```

Use `--module all` for the suite. Add `--apply` only after reviewing the plan. A target already containing a selected skill is never overwritten by `install`. `--action update` and `--action remove` require this installer's receipt and reject user-modified files. They also default to dry run. Unknown files are preserved. Do not edit the receipt.

The installer conservatively rejects known plugin-cache overlaps; supply `--plugin-cache /custom/cache` when the host uses a nondefault cache. It cannot prove the state of a remote host or unknown cache. Home and ancestor `.agents/skills` scopes are checked automatically; pass repeated `--other-skill-root` options for additional discovery directories. Resolve unknown remote/custom scope overlaps before installation.

## Codex plugin

The repository root includes `.agents/plugins/marketplace.json`, pointing to checked-in generated `dist/plugins/*` packages. The build also includes an independently usable marketplace inside `dist/`. On the locally observed Codex CLI 0.163.0, add the local marketplace root, then select a module or the full suite:

```sh
codex plugin marketplace add /absolute/path/to/agent-engineering-suite
codex plugin add agent-engineering-suite-history@agent-engineering-suite
# OR the complete suite (not both):
codex plugin add agent-engineering-suite@agent-engineering-suite
```

Use Codex's own plugin remove before replacing overlapping plugin forms; never manually edit/delete its cache. Preserve local edits before changing installations. CLI availability varies; consult `codex plugin --help` and the host's Plugins Directory. No install is implied by building a ZIP or passing our validator.

The generated `dist/` packages are intentionally versioned for Git marketplace distribution; do not hand-edit them. The builder protects changed output and regenerates deterministic artifacts from source skills. The local root marketplace route is tested. A remote Git marketplace command is not claimed verified until the publisher performs readback and remote installation. Public directory submission is separate and not automatic.

## Local integrity boundary

Install receipts are trusted local bookkeeping, not credentials or an authorization mechanism. Use one writer per target; adversarial concurrent filesystem mutation is outside this installer's guarantees. Symlinks, hardlinked managed files, unexpected files/directories and edited receipts/content are rejected before mutation where detectable. It does not promise an atomic multi-module transaction on I/O failure: inspect the reported partial state before retrying.
