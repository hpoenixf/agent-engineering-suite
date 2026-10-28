#!/usr/bin/env python3
"""Deterministic cross-conversation change audit for generic versioned scorecards.

Uses the existing 24-item and 28-item scorers as numeric authorities. A change
ledger is required for any item-level change, and product-change attribution is
separate from evidence discoveries and score calibration. Provider-free/read-only.
"""
from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = "aes-generic-calibration-v1"
SHA = re.compile(r"^[0-9a-f]{40}$")
KINDS = {"product_change", "new_evidence", "evidence_reclassification", "error_correction"}
OUTCOMES = {"pass", "partial", "failed", "blocked", "not_run", "unknown"}
AXES = {"goals", "benchmarks"}


class ReviewLockError(ValueError):
    pass


def check(cond: bool, message: str) -> None:
    if not cond:
        raise ReviewLockError(message)


def nonblank(value: Any, label: str, minimum: int = 12) -> str:
    check(isinstance(value, str) and len(value.strip()) >= minimum, label + ": substantive explanation required")
    return value


def num(value: Any) -> Decimal:
    check(value is not None and not isinstance(value, bool), "scored criterion missing numeric value")
    v = Decimal(str(value))
    check(v.is_finite() and Decimal(0) <= v <= Decimal(10), "invalid criterion score")
    return v


def r1(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def records(normalized: dict, axis: str) -> dict[str, dict]:
    if axis == "goals":
        rows = [row for group in normalized["goals"] for row in group["criteria"]]
        return {row["id"]: {"score": row.get("score"), "proof_level": row.get("stage"), "weight": row["weight"],
                            "evidence": row.get("evidence", []), "group": row["id"].split(".")[0]} for row in rows}
    rows = [row for group in normalized["axes"] for row in group["criteria"]]
    return {row["id"]: {"score": row.get("score"), "proof_level": row.get("proof_level"), "weight": row["weight"],
                        "evidence": row.get("evidence", []), "group": next(group["id"] for group in normalized["axes"] if row in group["criteria"])} for row in rows}


def check_evidence_record(ev: dict, target: str, current_date: str, paths: set[str]) -> None:
    check(isinstance(ev, dict), target + ": evidence record must be object")
    path = nonblank(ev.get("path"), target + " evidence path", 5)
    check(path in paths, target + ": evidence locator is not cited by the current criterion")
    check(bool(SHA.fullmatch(str(ev.get("record_revision", "")))), target + ": 40-char record_revision required")
    observed = ev.get("observed_version", {})
    check(isinstance(observed, dict), target + ": observed_version object required")
    sha = observed.get("commit")
    check(sha is None or bool(SHA.fullmatch(str(sha))), target + ": invalid observed commit")
    nonblank(observed.get("note"), target + " observed_version note")
    check(ev.get("outcome") in OUTCOMES, target + ": evidence outcome required")
    nonblank(ev.get("scope"), target + " evidence scope")
    nonblank(ev.get("limitations"), target + " evidence limitations")
    try:
        observed_at = date.fromisoformat(str(ev["observed_at"]))
        now_at = date.fromisoformat(current_date)
    except (ValueError, KeyError) as exc:
        raise ReviewLockError(target + ": valid evidence observation date required") from exc
    check(observed_at <= now_at, target + ": future evidence forbidden")
    # A same-Run file receipt is not a repeated independent task.
    if ev.get("independent_tasks"):
        nonblank(ev.get("denominator_scope"), target + " cohort denominator", 10)


def proof_signature(record: dict) -> tuple:
    observed = record.get("observed_version") or {}
    return (record.get("path"), record.get("record_revision"), record.get("observed_at"),
            observed.get("commit"), observed.get("source_tree"), record.get("artifact_hash"),
            record.get("level"), record.get("outcome"), record.get("scope"),
            tuple(record.get("methods", [])))


def validate_changes(prior: dict, current: dict, prior_raw: dict, current_raw: dict, changes: list,
                     axis: str) -> dict:
    check(prior["scale_fingerprint"] == current["scale_fingerprint"] and prior["scale_id"] == current["scale_id"],
          axis + ": rubric ID/weights changed; not numerically comparable")
    old_rows = records(prior, axis)
    new_rows = records(current, axis)
    check(set(old_rows) == set(new_rows) and len(new_rows) == (24 if axis == "goals" else 28), axis + ": fixed rubric incomplete")
    check(current["reviewed_at"] >= prior["reviewed_at"], axis + ": review date regressed")
    same_source = prior["source_commit"] == current["source_commit"]
    changed = {k for k in new_rows if (str(new_rows[k]["score"]), new_rows[k]["proof_level"]) !=
               (str(old_rows[k]["score"]), old_rows[k]["proof_level"])}
    declared = {c["criterion_id"] for c in changes}
    check(len(declared) == len(changes), axis + ": duplicate criterion change entry")
    check(declared == changed, axis + ": exact criterion change ledger required, missing=" +
          ",".join(sorted(changed - declared)) + "; extra=" + ",".join(sorted(declared - changed)))
    by_class = {k: {} for k in KINDS}
    audited = []
    current_evidence = {e["id"]: e for e in current_raw.get("evidence", [])} if axis == "goals" else {}
    for change in changes:
        item = change["criterion_id"]
        before, after = old_rows[item], new_rows[item]
        kind = change.get("kind")
        check(kind in KINDS, item + ": invalid attribution class")
        nonblank(change.get("reason"), item + " reason", 35)
        nonblank(change.get("scope"), item + " scope")
        nonblank(change.get("limitations"), item + " limitations")
        if kind == "product_change":
            check(not same_source, item + ": same SHA cannot be product improvement/regression")
        if kind in ("evidence_reclassification", "error_correction"):
            nonblank(change.get("prior_error"), item + " prior interpretation", 25)
            nonblank(change.get("adjudication"), item + " adjudication", 20)
        if kind in ("product_change", "new_evidence"):
            new_proof = change.get("new_evidence")
            check(isinstance(new_proof, list) and bool(new_proof), item + ": new positive/negative evidence required")
            allowed_paths = set(after["evidence"])
            for proof in new_proof:
                check_evidence_record(proof, item, current["reviewed_at"],
                                      {current_evidence[e]["path"] for e in allowed_paths if e in current_evidence}
                                      if axis == "goals" else allowed_paths)
            if axis == "goals":
                old_ids = set(before["evidence"])
                fresh = set(after["evidence"]) - old_ids
                check(bool(fresh), item + ": new evidence must introduce an independently indexed evidence ID")
                prior_evidence = {e["id"]: e for e in prior_raw.get("evidence", [])}
                earlier_signatures = {proof_signature(prior_evidence[e]) for e in before["evidence"] if e in prior_evidence}
                actual_fresh = [current_evidence[e] for e in fresh if e in current_evidence]
                check(any(proof_signature(e) not in earlier_signatures for e in actual_fresh),
                      item + ": renamed evidence ID is not new observation")
                def matches_record(proof, actual):
                    return (proof.get("path") == actual.get("path")
                            and proof.get("record_revision") == actual.get("record_revision")
                            and proof.get("observed_at") == actual.get("observed_at")
                            and proof.get("outcome") == actual.get("outcome")
                            and proof.get("scope") == actual.get("scope")
                            and proof.get("observed_version", {}).get("commit") ==
                                (actual.get("observed_version") or {}).get("commit"))
                check(any(matches_record(proof, item_record) for proof in new_proof for item_record in actual_fresh),
                      item + ": change proof must match newly cited goal evidence identity, scope and observation")
            if before["score"] is None or (after["score"] is not None and num(after["score"]) > num(before["score"])):
                check(any(proof["outcome"] == "pass" for proof in new_proof),
                      item + ": upward change needs a positive observation")
        # Unrated criteria are not silently counted as zero or reassigned weight.
        delta = ((num(after["score"]) - num(before["score"])) * Decimal(after["weight"]) / 100
                 if before["score"] is not None and after["score"] is not None else None)
        key = before["group"]
        if delta is not None:
            by_class[kind][key] = by_class[kind].get(key, Decimal(0)) + delta
        audited.append({"criterion_id": item, "kind": kind, "from": str(before["score"]),
                        "to": str(after["score"]), "proof_from": before["proof_level"],
                        "proof_to": after["proof_level"], "weighted_delta": r1(delta) if delta is not None else None,
                        "reason": change["reason"]})
    prior_policy = prior_raw.get("calibration_policy")
    current_policy = current_raw.get("calibration_policy")
    # Legacy schemas may omit fixed anchors. Preserve inputs but
    # never present a comparison against them as product improvement.
    check(current_policy == POLICY, axis + ": new assessment must declare calibration_policy=" + POLICY)
    policy_compatible = prior_policy == current_policy
    product = {g: r1(v) for g, v in by_class["product_change"].items()} if policy_compatible else {}
    return {"axis": axis, "prior_assessment": prior.get("assessment_id"),
            "current_assessment": current.get("assessment_id"), "same_source": same_source,
            "calibration_compatible": policy_compatible,
            "status": ("calibration_rebase_required" if not policy_compatible else
                       "same_source_adjudication" if same_source and changed else
                       "new_source_attributed" if changed else "unchanged"),
            "product_delta": product,
            "non_product_changes": {cls: {g: r1(v) for g, v in groups.items()} for cls, groups in by_class.items() if cls != "product_change"},
            "changes": sorted(audited, key=lambda e: e["criterion_id"]) }


def review(goal: dict | None, bench: dict | None, old_goal: dict | None,
           old_bench: dict | None, ledger: dict | None) -> dict:
    """Run original deterministic scorers first, then audit every changed item."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import goal_score
    import benchmark_score
    ledger = ledger or {"schema_version": 1, "changes": []}
    check(ledger.get("schema_version") == 1 and isinstance(ledger.get("changes"), list), "invalid change-ledger schema")
    check(bool(goal or bench), "at least one assessment required")
    target: dict[str, Any] = {"policy": POLICY, "axes": {}}
    if goal is not None:
        check(old_goal is not None, "previous goal assessment required")
        p, c = goal_score.evaluate(old_goal), goal_score.evaluate(goal)
        parts = [x for x in ledger["changes"] if x.get("axis") == "goals"]
        target["axes"]["goals"] = {"scores": {g["id"]: g["score"] for g in c["goals"]},
                                   "audit": validate_changes(p, c, old_goal, goal, parts, "goals")}
    if bench is not None:
        check(old_bench is not None, "previous benchmark assessment required")
        p, c = benchmark_score.evaluate(old_bench), benchmark_score.evaluate(bench)
        parts = [x for x in ledger["changes"] if x.get("axis") == "benchmarks"]
        target["axes"]["benchmarks"] = {"scores": {a["id"]: {"capability": a["capability"],
                                 "evidence_maturity": a["evidence_maturity"]} for a in c["axes"]},
                                 "audit": validate_changes(p, c, old_bench, bench, parts, "benchmarks")}
    requested = {"goals" if goal else None, "benchmarks" if bench else None} - {None}
    check(all(x.get("axis") in requested for x in ledger["changes"]), "unrequested axis in change ledger")
    # No global average; these scores measure different goals and reference envelopes.
    return target


def cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--goals", type=Path)
    p.add_argument("--benchmarks", type=Path)
    p.add_argument("--previous-goals", type=Path)
    p.add_argument("--previous-benchmarks", type=Path)
    p.add_argument("--changes", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    try:
        rd = lambda path: json.loads(path.read_text(encoding="utf-8")) if path else None
        res = review(rd(args.goals), rd(args.benchmarks), rd(args.previous_goals) if args.goals else None,
                     rd(args.previous_benchmarks) if args.benchmarks else None, rd(args.changes))
        output = json.dumps(res, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    except (ReviewLockError, ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print("scorecard-review-lock: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(cli())

