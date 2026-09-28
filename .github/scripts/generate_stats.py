#!/usr/bin/env python3

import html
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


API_ROOT = "https://api.github.com"
USER = os.environ.get("GITHUB_USER", "wondonghwi")
TOKEN = os.environ.get("GH_TOKEN")
OUTPUT = Path("profile/stats.svg")


def github_api(path: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "wondonghwi-profile-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def search_count(query: str) -> int:
    encoded_query = urllib.parse.quote(query)
    return github_api(f"/search/issues?q={encoded_query}&per_page=1")["total_count"]


def render_svg(stats: list[tuple[str, int]]) -> str:
    title = html.escape(f"{USER}'s GitHub Stats")
    rows = []
    for index, (label, value) in enumerate(stats):
        column = index % 2
        row = index // 2
        x = 28 + column * 245
        y = 82 + row * 44
        rows.append(
            f'<text x="{x}" y="{y}" class="value">{value:,}</text>'
            f'<text x="{x + 52}" y="{y}" class="label">{html.escape(label)}</text>'
        )

    return f'''<svg width="495" height="190" viewBox="0 0 495 190" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Public GitHub activity for {html.escape(USER)}</desc>
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #fe428e; }}
    .value {{ font: 700 16px 'Segoe UI', Ubuntu, Sans-Serif; fill: #f8f8f2; }}
    .label {{ font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #a9fef7; }}
    .footer {{ font: 400 11px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
  </style>
  <rect x="0.5" y="0.5" width="494" height="189" rx="6" fill="#141321" stroke="#e4e2e2"/>
  <text x="28" y="38" class="header">{title}</text>
  <line x1="28" y1="53" x2="467" y2="53" stroke="#30363d"/>
  {''.join(rows)}
  <text x="28" y="172" class="footer">Public activity · Generated with the GitHub API</text>
</svg>
'''


def main() -> None:
    user = github_api(f"/users/{urllib.parse.quote(USER)}")
    stats = [
        ("Public repositories", user["public_repos"]),
        ("Merged pull requests", search_count(f"author:{USER} is:pr is:merged")),
        ("Followers", user["followers"]),
        ("Issues opened", search_count(f"author:{USER} is:issue")),
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_svg(stats), encoding="utf-8")


if __name__ == "__main__":
    main()
