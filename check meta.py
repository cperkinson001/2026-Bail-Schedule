#!/usr/bin/env python3
"""
Compares freshly-computed hashes of the two source PDFs against what's stored
in meta.json. Writes an updated meta.json and sets a `changed` output for the
GitHub Actions workflow to consume.

- First run (no hashes stored yet): saves the hashes as a baseline. Does NOT
  flag a change, since there's nothing to compare against yet.
- Later runs: if either hash differs from what's stored, flags `changed=true`,
  records `last_changed`, and sets `update_pending=true` (cleared manually
  once someone updates data.js and edits meta.json).
- `last_checked` is updated on every run regardless, so the app can always
  show how recently the source was verified.
"""
import argparse
import json
import os
from datetime import datetime, timezone

META_PATH = os.path.join(os.path.dirname(__file__), "..", "meta.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--felony-hash", required=True)
    parser.add_argument("--misd-hash", required=True)
    args = parser.parse_args()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            meta = json.load(f)
    else:
        meta = {}

    prev_felony_hash = meta.get("felony_pdf_sha256") or None
    prev_misd_hash = meta.get("misdemeanor_pdf_sha256") or None

    is_baseline = prev_felony_hash is None or prev_misd_hash is None
    changed = (not is_baseline) and (
        prev_felony_hash != args.felony_hash or prev_misd_hash != args.misd_hash
    )

    meta["felony_pdf_sha256"] = args.felony_hash
    meta["misdemeanor_pdf_sha256"] = args.misd_hash
    meta["last_checked"] = now

    if changed:
        meta["last_changed"] = now
        meta["update_pending"] = True
    elif is_baseline:
        meta.setdefault("last_changed", now)
        meta.setdefault("update_pending", False)
    # if unchanged and not baseline, leave last_changed / update_pending as-is

    meta.setdefault("schedule_effective_date", "2026-01-01")

    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")

    print(f"baseline={is_baseline} changed={changed}")


if __name__ == "__main__":
    main()
