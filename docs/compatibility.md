# Compatibility and evidence boundary

- Toolchain baseline: Node >=26.11.1 <27, matching the retained public toolkit; Python 3 standard library for optional maturity calculators. No runtime npm dependencies.
- Plugin metadata: Agent Plugins schema 1.0.0 plus generated Codex compatibility manifest. Official documentation: https://developers.openai.com/plugins/build/plugins
- Standalone discovery: project/user `.agents/skills`; official guidance: https://learn.chatgpt.com/docs/build-skills
- Local CLI observed: codex-cli 0.163.0 supports `plugin add/remove` and marketplace management according to its own help. Earlier minimum version is not established.
- Platform-neutral path handling is intended. Linux is the current validation environment; macOS and Windows are not yet tested.
- Offline build validation is not native installation, skill invocation, semantic correctness, real-model acceptance or public-directory approval. Native isolated module/full install, list, byte readback and remove passed on Codex 0.163.0; see [validation record](validation.md).
- Full and module installs overlap skill names. Use one form for each module; do not install both and expect Codex to merge them. Installer checks the default local plugin cache conservatively; custom cache locations must be supplied.
- No account integrations, hook execution, credentials or permissions are bundled. File-only core modules cannot invoke unavailable host tools.
