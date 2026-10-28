# Generic optional calculators

The additional `../scripts/review_lock.py` audits exact item-change ledgers, same-evidence drift, source attribution and scale compatibility using these generic scorers. Previous assessments must be supplied explicitly; no private defaults remain. It validates recorded evidence relationships, not the truth of external observations.

These self-contained Python standard-library tools retain deterministic scoring and evidence-review mechanisms with new generic profiles, without private baselines or automatic publication:

- `../scripts/goal_score.py`: 24 criteria, scoped source evidence, cohort denominators, scale fingerprints and baseline comparisons; [rubric](three-goal-rubric.json).
- `../scripts/benchmark_score.py`: 28 criteria in three independent capability-reference axes, proof maturity and frozen weight fingerprints; [rubric](comparator-rubric.json).
- `../scripts/strategic_score.py`: 16 criteria, 45/30/25 technology pillars and independent business value, duplicate-key/weight/cached-total checks and optional strict evidence; [rubric](strategic-focus-rubric.json).

Resolve scripts relative to this skill and run `python3 <script> --help`. Supply an explicit assessment file; there is no default private assessment. They do not access network, Git, models or CI. Optional `--output` writes only the explicitly chosen report.

This is an adapted toolkit, not a claim of full parity with private historical score migration, source discovery or publication guards. No private module mapping, ownership code, timetable, internal locator or comparator benchmark is shipped. Profile IDs changed deliberately: historical assessments are incompatible. Numeric validation is not semantic verification; a strict evidence field check cannot prove the referenced execution occurred. Generic rubric uses a different scale and must not be compared against these profiles.
