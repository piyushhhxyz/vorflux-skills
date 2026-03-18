#!/usr/bin/env python3
"""
gen_changelog.py — Generate CHANGELOG.md entry from Conventional Commits git log
Usage: python3 gen_changelog.py [version] [--since <tag>]
"""

import subprocess
import sys
import re
import argparse
from datetime import date
from collections import defaultdict
from pathlib import Path


COMMIT_TYPES = {
    "feat":     ("Features",          "✨"),
    "fix":      ("Bug Fixes",         "🐛"),
    "perf":     ("Performance",       "⚡"),
    "refactor": ("Refactoring",       "♻️"),
    "docs":     ("Documentation",     "📚"),
    "test":     ("Tests",             "✅"),
    "build":    ("Build System",      "🏗️"),
    "ci":       ("CI/CD",             "👷"),
    "chore":    ("Chores",            "🔧"),
    "style":    ("Style",             "💄"),
    "revert":   ("Reverts",           "⏪"),
}

# Types to include in user-facing changelog
PUBLIC_TYPES = {"feat", "fix", "perf", "refactor", "docs"}

BREAKING_PATTERN = re.compile(r"BREAKING[- ]CHANGE[S]?:\s*(.+)", re.IGNORECASE)


def run(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return ""


def get_commits(since_tag: str = None) -> list[dict]:
    """Fetch commits since last tag or a specific tag."""
    if since_tag:
        log_range = f"{since_tag}..HEAD"
    else:
        last_tag = run("git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo ''")
        log_range = f"{last_tag}..HEAD" if last_tag else "HEAD"

    # Format: hash|subject|body|author
    fmt = "%H|%s|%b|%an"
    raw = run(f'git log {log_range} --format="{fmt}" --no-merges')
    if not raw:
        return []

    commits = []
    for line in raw.splitlines():
        if "|" not in line:
            continue
        parts = line.split("|", 3)
        if len(parts) < 2:
            continue
        sha, subject = parts[0], parts[1]
        body   = parts[2] if len(parts) > 2 else ""
        author = parts[3] if len(parts) > 3 else ""

        # Parse conventional commit
        m = re.match(r"^(\w+)(\(([^)]+)\))?(!)?\s*:\s*(.+)$", subject)
        if not m:
            commits.append({"type": "other", "scope": None, "breaking": False,
                            "message": subject, "sha": sha[:8], "author": author})
            continue

        commit_type  = m.group(1).lower()
        scope        = m.group(3)
        breaking_tag = bool(m.group(4))
        message      = m.group(5).strip()

        # Check body for BREAKING CHANGE
        breaking_msg = ""
        bm = BREAKING_PATTERN.search(body)
        if bm:
            breaking_msg = bm.group(1)

        commits.append({
            "type":         commit_type,
            "scope":        scope,
            "breaking":     breaking_tag or bool(bm),
            "breaking_msg": breaking_msg or (message if breaking_tag else ""),
            "message":      message,
            "sha":          sha[:8],
            "author":       author,
        })

    return commits


def group_commits(commits: list[dict]) -> dict:
    groups = defaultdict(list)
    breaking = []

    for c in commits:
        if c["breaking"]:
            breaking.append(c)
        if c["type"] in COMMIT_TYPES:
            groups[c["type"]].append(c)
        elif c["type"] not in ("other",):
            groups["chore"].append(c)

    return {"breaking": breaking, **dict(groups)}


def format_commit(c: dict) -> str:
    scope = f"**{c['scope']}:** " if c.get("scope") else ""
    return f"- {scope}{c['message']} ([`{c['sha']}`](../../commit/{c['sha']}))"


def render_entry(version: str, groups: dict, include_all: bool = False) -> str:
    today = date.today().strftime("%Y-%m-%d")
    tag   = version or "Unreleased"
    anchor = version.lstrip("v") if version else "unreleased"
    lines = [f"## [{tag}] — {today}", ""]

    # Breaking changes first
    if groups.get("breaking"):
        lines.append("### ⚠️ Breaking Changes")
        lines.append("")
        for c in groups["breaking"]:
            msg = c.get("breaking_msg") or c["message"]
            lines.append(f"- **{msg}**")
        lines.append("")

    # Main sections
    type_order = ["feat", "fix", "perf", "refactor", "docs", "test", "build", "ci", "chore"]
    for t in type_order:
        commits = groups.get(t, [])
        if not commits:
            continue
        if not include_all and t not in PUBLIC_TYPES:
            continue
        label, emoji = COMMIT_TYPES.get(t, (t.title(), "•"))
        lines.append(f"### {emoji} {label}")
        lines.append("")
        for c in commits:
            lines.append(format_commit(c))
        lines.append("")

    return "\n".join(lines)


def render_release_notes(version: str, groups: dict) -> str:
    """Shorter, user-facing release notes for GitHub release body."""
    lines = [f"## What's Changed in {version or 'this release'}", ""]

    if groups.get("breaking"):
        lines.append("### ⚠️ Breaking Changes")
        for c in groups["breaking"]:
            lines.append(f"- {c.get('breaking_msg') or c['message']}")
        lines.append("")

    features = groups.get("feat", [])
    fixes    = groups.get("fix", [])

    if features:
        lines.append(f"### ✨ New Features ({len(features)})")
        for c in features[:8]:
            scope = f"**{c['scope']}:** " if c.get("scope") else ""
            lines.append(f"- {scope}{c['message']}")
        if len(features) > 8:
            lines.append(f"- ...and {len(features) - 8} more")
        lines.append("")

    if fixes:
        lines.append(f"### 🐛 Bug Fixes ({len(fixes)})")
        for c in fixes[:6]:
            scope = f"**{c['scope']}:** " if c.get("scope") else ""
            lines.append(f"- {scope}{c['message']}")
        lines.append("")

    total = sum(len(v) for v in groups.values() if isinstance(v, list))
    lines.append(f"**Full changelog:** {total} commits")

    return "\n".join(lines)


def update_changelog(new_entry: str):
    changelog_path = Path("CHANGELOG.md")
    if changelog_path.exists():
        existing = changelog_path.read_text()
        # Insert after the header (first H1 or first blank line after H1)
        if "## [" in existing:
            insert_at = existing.index("## [")
            new_content = existing[:insert_at] + new_entry + "\n\n" + existing[insert_at:]
        else:
            new_content = existing.rstrip() + "\n\n" + new_entry + "\n"
    else:
        header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        new_content = header + new_entry + "\n"

    changelog_path.write_text(new_content)
    print(f"✅  Updated CHANGELOG.md")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", nargs="?", default=None)
    parser.add_argument("--since", default=None)
    parser.add_argument("--all",   action="store_true", help="Include all commit types")
    parser.add_argument("--no-update", action="store_true", help="Don't update CHANGELOG.md")
    args = parser.parse_args()

    commits = get_commits(since_tag=args.since)
    if not commits:
        print("No new commits found since last tag.")
        sys.exit(0)

    groups = group_commits(commits)
    entry  = render_entry(args.version, groups, include_all=args.all)
    notes  = render_release_notes(args.version, groups)

    # Write changelog entry
    Path("CHANGELOG_ENTRY.md").write_text(entry)
    print(f"✅  CHANGELOG_ENTRY.md ({len(commits)} commits)")

    # Write release notes
    Path("RELEASE_NOTES.md").write_text(notes)
    print(f"✅  RELEASE_NOTES.md")

    # Update main CHANGELOG.md
    if not args.no_update:
        update_changelog(entry)

    print()
    print(entry)


if __name__ == "__main__":
    main()
