#!/usr/bin/env python3
"""Generate README.md for Slimefun5 addon repositories.

Usage: python3 generate-readme.py --repository Slimefun5/SlimeTinker

Reads from CWD:
  gradle.properties    -> description
  .github/docs-config.yml -> logo, java, paper, gradle_plugin, description (override)
  CONTENT.md           -> custom content (features, credits, etc.)

Fetches from GitHub API:
  Latest tag for the repository
"""

import argparse
import json
import os
import sys
import urllib.request


def parse_config(path):
    """Parse flat key-value YAML without requiring pyyaml."""
    config = {}
    if not os.path.exists(path):
        return config
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value:
                    config[key] = value
    return config


def read_gradle_description():
    if not os.path.exists("gradle.properties"):
        return ""
    with open("gradle.properties") as f:
        for line in f:
            line = line.strip().replace("\r", "")
            if line.startswith("description="):
                return line.split("=", 1)[1]
    return ""


def fetch_latest_tag(repository):
    url = f"https://api.github.com/repos/{repository}/tags"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "readme-generator"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if isinstance(data, list) and len(data) > 0:
                return data[0]["name"]
    except Exception:
        pass
    return "v1.0.0"


def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path) as f:
        return f.read().strip()


def main():
    parser = argparse.ArgumentParser(description="Generate README.md")
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()

    org_name, repo_name = args.repository.split("/")
    config = parse_config(".github/docs-config.yml")

    description = (
        config.get("description")
        or read_gradle_description()
        or "A Slimefun 5 Addon."
    )
    java = config.get("java", "25")
    paper = config.get("paper", "1.16.* - 26.1.*")
    gradle_plugin = config.get("gradle_plugin", "1.8.2.1")
    logo = config.get("logo", "")
    latest_tag = fetch_latest_tag(args.repository)
    content = read_file("CONTENT.md")

    sections = []

    if logo:
        sections.append(
            f'<p align="center">\n'
            f'<img width="800" src="{logo}"><br><br>\n'
            f"</p>"
        )

    sections.append(f"# {repo_name}")

    sections.append(
        f"[![Build Status](https://Slimefun5.github.io/builds/{org_name}/{repo_name}/stable/badge.svg)]"
        f"(https://Slimefun5.github.io/builds/{org_name}/{repo_name}/stable)\n"
        f"![GitHub Downloads (all assets, all releases)]"
        f"(https://img.shields.io/github/downloads/{org_name}/{repo_name}/total)\n"
        f"[![GitHub Followers](https://img.shields.io/github/followers/{org_name}?style=social)]"
        f"(https://github.com/{org_name})\n"
        f"[![GitHub Stars](https://img.shields.io/github/stars/{org_name}/{repo_name}?style=social)]"
        f"(https://github.com/{org_name}/{repo_name})"
    )

    sections.append(description)

    is_core = repo_name.lower() in ("slimefun5", "slimefun")
    req_lines = f"## Requirements\n- Java {java}\n- Paper {paper}"
    if not is_core:
        req_lines += "\n- [Slimefun 5](https://github.com/Slimefun5/Slimefun5)"
    sections.append(req_lines)

    if content:
        sections.append(content)

    sections.append(
        f"## Developer API\n\n"
        f"You can easily depend on this project using "
        f"[github-gradle](https://github.com/intisy/github-gradle).\n\n"
        f"In your `build.gradle.kts`:\n\n"
        f"```kotlin\n"
        f"plugins {{\n"
        f'    id("io.github.intisy.github-gradle") version "{gradle_plugin}"\n'
        f"}}\n\n"
        f"dependencies {{\n"
        f'    "githubCompileOnly"("{org_name}:{repo_name}:{latest_tag}")\n'
        f"}}\n"
        f"```"
    )

    sections.append(
        f"## Wiki\n\n"
        f"[Read more on the Slimefun Wiki...](https://github.com/Slimefun5/Wiki/wiki/{repo_name})"
    )

    sections.append(
        f"## Discord\n\n"
        f"You can find Slimefun's community on Discord! Click the badge below to join the server for suggestions/questions or other discussions about this plugin.\n\n"
        f'<p align="center">\n'
        f'  <a href="https://discord.gg/fsD4Bkh">\n'
        f'    <img src="https://discordapp.com/api/guilds/738626600539160576/widget.png?style=banner2" alt="Discord"/>\n'
        f'  </a>\n'
        f'</p>'
    )

    sections.append(
        f"## License\n\n"
        f"This project is open-source and licensed under the MIT License."
    )

    readme = "\n\n".join(sections) + "\n"
    with open("README.md", "w") as f:
        f.write(readme)

    print(f"Generated README.md for {args.repository} (tag: {latest_tag})")


if __name__ == "__main__":
    main()
