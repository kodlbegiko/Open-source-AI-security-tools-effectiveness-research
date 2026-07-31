#!/usr/bin/env python3
"""Collect first-party GitHub metadata for the candidate tool landscape.

This script does not score effectiveness. It records repository identity,
license, branch-head SHA, archive state, activity timestamps and latest release
metadata from GitHub's API so later selection decisions are based on current,
versioned facts rather than search snippets or popularity rankings.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com"
USER_AGENT = "open-source-ai-security-effectiveness-research/0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def api_get(path: str, token: str) -> tuple[int, dict[str, Any] | list[Any] | None]:
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 404, None
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {path}: {body[:500]}") from exc


def collect_candidate(seed: dict[str, Any], token: str, retrieved_at: str) -> dict[str, Any]:
    repository = seed["repository"]
    status, repo = api_get(f"/repos/{repository}", token)
    if status != 200 or not isinstance(repo, dict):
        return {
            **seed,
            "retrieved_at": retrieved_at,
            "verification_status": "REPOSITORY_NOT_FOUND",
            "error": f"GitHub repository lookup returned HTTP {status}",
        }

    canonical_name = repo["full_name"]
    default_branch = repo["default_branch"]
    commit_status, commit = api_get(
        f"/repos/{canonical_name}/commits/{default_branch}", token
    )
    release_status, release = api_get(f"/repos/{canonical_name}/releases/latest", token)

    license_data = repo.get("license") or {}
    latest_release: dict[str, Any] | None
    if release_status == 200 and isinstance(release, dict):
        latest_release = {
            "tag_name": release.get("tag_name"),
            "name": release.get("name"),
            "published_at": release.get("published_at"),
            "draft": release.get("draft"),
            "prerelease": release.get("prerelease"),
            "html_url": release.get("html_url"),
            "target_commitish": release.get("target_commitish"),
        }
    else:
        latest_release = None

    head_sha = commit.get("sha") if isinstance(commit, dict) else None
    head_date = None
    if isinstance(commit, dict):
        head_date = (
            commit.get("commit", {})
            .get("committer", {})
            .get("date")
        )

    return {
        **seed,
        "retrieved_at": retrieved_at,
        "verification_status": "VERIFIED",
        "repository": canonical_name,
        "repository_url": repo.get("html_url"),
        "description": repo.get("description"),
        "homepage": repo.get("homepage"),
        "visibility": repo.get("visibility"),
        "archived": repo.get("archived"),
        "disabled": repo.get("disabled"),
        "fork": repo.get("fork"),
        "default_branch": default_branch,
        "default_branch_head_sha": head_sha,
        "default_branch_head_date": head_date,
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "license_spdx": license_data.get("spdx_id"),
        "license_name": license_data.get("name"),
        "has_releases": latest_release is not None,
        "latest_release": latest_release,
        "source": "GitHub REST API",
    }


def flatten_for_csv(row: dict[str, Any]) -> dict[str, Any]:
    release = row.get("latest_release") or {}
    return {
        "name": row.get("name"),
        "repository": row.get("repository"),
        "repository_url": row.get("repository_url"),
        "category": row.get("category"),
        "tool_type": row.get("tool_type"),
        "primary_task": row.get("primary_task"),
        "verification_status": row.get("verification_status"),
        "archived": row.get("archived"),
        "fork": row.get("fork"),
        "license_spdx": row.get("license_spdx"),
        "default_branch": row.get("default_branch"),
        "default_branch_head_sha": row.get("default_branch_head_sha"),
        "default_branch_head_date": row.get("default_branch_head_date"),
        "pushed_at": row.get("pushed_at"),
        "latest_release_tag": release.get("tag_name"),
        "latest_release_published_at": release.get("published_at"),
        "latest_release_prerelease": release.get("prerelease"),
        "retrieved_at": row.get("retrieved_at"),
        "error": row.get("error"),
    }


def render_markdown(rows: list[dict[str, Any]], retrieved_at: str) -> str:
    categories = Counter(row["category"] for row in rows)
    verified = sum(row.get("verification_status") == "VERIFIED" for row in rows)
    archived = sum(row.get("archived") is True for row in rows)
    lines = [
        "# Open-Source AI Security Tool Landscape",
        "",
        f"- Retrieved: `{retrieved_at}`",
        "- Source: GitHub REST API and official repositories",
        f"- Candidate repositories: **{len(rows)}**",
        f"- Verified repositories: **{verified}**",
        f"- Categories: **{len(categories)}**",
        f"- Archived repositories observed: **{archived}**",
        "",
        "> Inclusion in this landscape is not an effectiveness endorsement and does not imply formal evaluation.",
        "",
        "## Category coverage",
        "",
        "| Category | Candidates |",
        "|---|---:|",
    ]
    for category, count in sorted(categories.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend([
        "",
        "## Candidates",
        "",
        "| Tool | Category | Repository | License | Head SHA | Latest release | Archived | Status |",
        "|---|---|---|---|---|---|---:|---|",
    ])
    for row in rows:
        release = row.get("latest_release") or {}
        sha = row.get("default_branch_head_sha") or "—"
        tag = release.get("tag_name") or "—"
        lines.append(
            "| {name} | {category} | `{repo}` | {license} | `{sha}` | `{tag}` | {archived} | {status} |".format(
                name=row.get("name", "—"),
                category=row.get("category", "—"),
                repo=row.get("repository", "—"),
                license=row.get("license_spdx") or "UNKNOWN",
                sha=sha[:12] if sha != "—" else sha,
                tag=tag,
                archived=str(row.get("archived")).lower() if row.get("archived") is not None else "—",
                status=row.get("verification_status", "UNKNOWN"),
            )
        )

    lines.extend([
        "",
        "## Interpretation limits",
        "",
        "- Repository activity, releases and licensing are feasibility evidence, not security-effectiveness evidence.",
        "- Different categories, defense locations and output semantics must not be combined into one effectiveness ranking.",
        "- Exact formal tool versions will be frozen only after Gate 1 selection and before protocol freeze.",
        "- Missing releases do not imply an ineffective tool; they indicate a packaging or versioning characteristic.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    token = os.environ.get("GH_TOKEN")
    if not token:
        print("GH_TOKEN is required", file=sys.stderr)
        return 2

    seed_path = Path(os.environ.get("SEED_PATH", "data/tool-candidate-seeds.json"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", "generated/tool-landscape"))
    output_dir.mkdir(parents=True, exist_ok=True)

    seed_document = json.loads(seed_path.read_text(encoding="utf-8"))
    seeds = seed_document["candidates"]
    retrieved_at = utc_now()

    rows: list[dict[str, Any]] = []
    for index, seed in enumerate(seeds, start=1):
        print(f"[{index}/{len(seeds)}] {seed['repository']}", file=sys.stderr)
        rows.append(collect_candidate(seed, token, retrieved_at))
        time.sleep(0.05)

    document = {
        "schema_version": "1.0",
        "retrieved_at": retrieved_at,
        "source": "GitHub REST API",
        "candidate_count": len(rows),
        "verified_count": sum(row.get("verification_status") == "VERIFIED" for row in rows),
        "category_count": len({row["category"] for row in rows}),
        "candidates": rows,
    }
    (output_dir / "tool-candidates.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    csv_rows = [flatten_for_csv(row) for row in rows]
    with (output_dir / "tool-candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    (output_dir / "tool-landscape.md").write_text(
        render_markdown(rows, retrieved_at), encoding="utf-8"
    )

    unresolved = [row for row in rows if row.get("verification_status") != "VERIFIED"]
    summary = {
        "candidate_count": len(rows),
        "verified_count": len(rows) - len(unresolved),
        "unresolved_count": len(unresolved),
        "category_count": len({row["category"] for row in rows}),
        "archived_count": sum(row.get("archived") is True for row in rows),
    }
    (output_dir / "collection-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
