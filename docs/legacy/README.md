# Preserved public source history

These two Git bundles retain the original public repositories' commits and refs, including v0.1.0 tags. They are historical recovery artifacts, not another live implementation to edit. Current implementation is under the suite's `skills/` directory.

- [OpenSpec source](../../skills/aes-spec-flow/toolkit/README.md), bundle `openspec-evidence-kit.bundle`.
- [History source](../../skills/aes-history/SKILL.md), bundle `engineering-history-skill.bundle`.

See `preservation-manifest.json` for exact original heads, tags, SHA-256 hashes, object counts and verification observations. Release JSON records preserve public release metadata; historical source URLs may no longer resolve after repository retirement. Deletion/retirement of old repositories is a separate maintainer action and is not implied by these files.

## Restore to a new directory only

Check the bundle hash against the manifest first. In an existing Git repository, `git bundle verify /path/to/openspec-evidence-kit.bundle` verifies prerequisites and bundle structure. `git bundle list-heads /path/to/openspec-evidence-kit.bundle` lists preserved refs without modifying a worktree.

When an additional checkout is permitted, use `git clone /path/to/openspec-evidence-kit.bundle /new/empty/destination` (or the history bundle). Inspect the expected head and tag from the manifest. Never run reset/clean or restore over an active project. A recovered historical version is not the latest suite and does not prove current-work recoverability.

Both original public bundles contain complete history without external prerequisites; they were verified before copying and their copied byte hashes matched. They contain no private parent commits according to the recorded pre-migration audit.
