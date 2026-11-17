"""Count verifier interventions of swarm_verified (bonus B3).

Runs swarm_verified on every (claim, seed) with a fresh SQLite per trial, reads
its trace, and counts `verifier_override` events and which fields disagreed.

    python -m bonus.verifier_stats --out reports/bonus_verifier.json

Default: public set and bonus adversarial set, seeds 11,22,33,44,55.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from lab8.config_loader import repo_path
from lab8.console import utf8_stdio
from lab8.db import init_store, load_json, load_jsonl

from bonus.swarm_verified import run_claim

SETS = {
    "public": (repo_path("data", "public_claims.jsonl"), repo_path("data", "public_world_state.json")),
    "adversarial": (repo_path("bonus", "cases.jsonl"), repo_path("bonus", "world.json")),
}


def collect(cases: Path, world_path: Path, seeds: list[int]) -> dict[str, Any]:
    claims = load_jsonl(cases)
    world = load_json(world_path)
    rows = []
    fields: Counter[str] = Counter()
    with tempfile.TemporaryDirectory(prefix="bonus-verifier-", ignore_cleanup_errors=True) as tmp:
        for claim in claims:
            for seed in seeds:
                store = Path(tmp) / f"{claim['claim_id']}-{seed}.sqlite"
                init_store(store, world, claims).close()
                result = run_claim(claim["claim_id"], seed=seed, store_path=str(store))
                events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
                overrides = [e["payload"] for e in events if e["kind"] == "verifier_override"]
                for payload in overrides:
                    fields.update(payload["mismatches"].keys())
                if overrides:
                    rows.append(
                        {
                            "claim_id": claim["claim_id"],
                            "seed": seed,
                            "run_id": result.run_id,
                            "status": result.status,
                            "proposal_amount": result.proposal_amount,
                            "mismatched_fields": sorted(overrides[0]["mismatches"]),
                        }
                    )
    trials = len(claims) * len(seeds)
    return {
        "trials": trials,
        "verifier_overrides": len(rows),
        "override_rate": len(rows) / trials if trials else None,
        "fields": dict(fields),
        "overridden_trials": rows,
    }


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description="Count swarm_verified verifier interventions")
    parser.add_argument("--seeds", default="11,22,33,44,55")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    seeds = [int(part) for part in args.seeds.split(",") if part.strip()]
    report = {"shape": "swarm_verified", "seeds": seeds, "sets": {}}
    for name, (cases, world) in SETS.items():
        report["sets"][name] = collect(Path(cases), Path(world), seeds)
        stats = report["sets"][name]
        print(f"{name:<12} trials={stats['trials']:<4} overrides={stats['verifier_overrides']:<3} fields={stats['fields']}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
