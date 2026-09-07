#!/usr/bin/env python3
"""Synchronize canonical GitHub labels across a GitHub App installation."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import yaml

API_VERSION = "2022-11-28"
DEFAULT_API_URL = "https://api.github.com"
PAGE_SIZE = 100
COLOR_RE = re.compile(r"^[0-9a-fA-F]{6}$")
LOGGER = logging.getLogger("label-sync")


class ConfigError(ValueError):
    """Raised when the canonical label configuration is invalid."""


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API returns an unexpected response."""


@dataclass(frozen=True)
class LabelDefinition:
    name: str
    color: str
    description: str = ""


@dataclass
class RepoStats:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    kept: int = 0


@dataclass
class RunStats:
    repositories_succeeded: int = 0
    repositories_failed: int = 0
    repositories_skipped: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    kept: int = 0

    def add_repo(self, stats: RepoStats) -> None:
        self.repositories_succeeded += 1
        self.created += stats.created
        self.updated += stats.updated
        self.unchanged += stats.unchanged
        self.kept += stats.kept


class GitHubClient:
    def __init__(self, token: str, api_url: str = DEFAULT_API_URL) -> None:
        if not token:
            raise ValueError("GitHub token must not be empty")
        self._token = token
        self._api_url = api_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, str]]:
        url = f"{self._api_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"

        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "User-Agent": "yohi-central-label-sync",
                "X-GitHub-Api-Version": API_VERSION,
            },
        )

        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read()
                body = json.loads(raw.decode("utf-8")) if raw else None
                headers = {key.lower(): value for key, value in response.headers.items()}
                return body, headers
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(raw).get("message", raw)
            except json.JSONDecodeError:
                message = raw
            raise GitHubAPIError(
                f"GitHub API {method} {path} failed with HTTP {exc.code}: {message}"
            ) from exc
        except URLError as exc:
            raise GitHubAPIError(
                f"GitHub API {method} {path} failed: {exc.reason}"
            ) from exc

    def list_installation_repositories(self) -> list[dict[str, Any]]:
        repositories: list[dict[str, Any]] = []
        page = 1
        while True:
            body, _ = self.request(
                "GET",
                "/installation/repositories",
                query={"per_page": PAGE_SIZE, "page": page},
            )
            if not isinstance(body, dict) or not isinstance(body.get("repositories"), list):
                raise GitHubAPIError("Unexpected response from installation repositories API")
            batch = body["repositories"]
            repositories.extend(batch)
            if len(batch) < PAGE_SIZE:
                return repositories
            page += 1

    def list_labels(self, full_name: str) -> list[dict[str, Any]]:
        owner, repo = split_full_name(full_name)
        labels: list[dict[str, Any]] = []
        page = 1
        while True:
            body, _ = self.request(
                "GET",
                f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/labels",
                query={"per_page": PAGE_SIZE, "page": page},
            )
            if not isinstance(body, list):
                raise GitHubAPIError(f"Unexpected labels response for {full_name}")
            labels.extend(body)
            if len(body) < PAGE_SIZE:
                return labels
            page += 1

    def create_label(self, full_name: str, label: LabelDefinition) -> None:
        owner, repo = split_full_name(full_name)
        self.request(
            "POST",
            f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/labels",
            payload={
                "name": label.name,
                "color": label.color,
                "description": label.description,
            },
        )

    def update_label(
        self,
        full_name: str,
        current_name: str,
        label: LabelDefinition,
    ) -> None:
        owner, repo = split_full_name(full_name)
        self.request(
            "PATCH",
            f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/labels/{quote(current_name, safe='')}",
            payload={
                "new_name": label.name,
                "color": label.color,
                "description": label.description,
            },
        )


def split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Invalid repository full_name: {full_name!r}")
    return parts[0], parts[1]


def load_config(path: Path) -> list[LabelDefinition]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Configuration file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Top-level YAML value must be a mapping")
    if data.get("version") != 1:
        raise ConfigError("version must be exactly 1")

    raw_labels = data.get("labels")
    if not isinstance(raw_labels, list):
        raise ConfigError("labels must be a list")

    labels: list[LabelDefinition] = []
    seen_names: set[str] = set()
    errors: list[str] = []

    for index, item in enumerate(raw_labels, start=1):
        prefix = f"labels[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be a mapping")
            continue

        name = item.get("name")
        color = item.get("color")
        description = item.get("description", "")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}.name: must be a non-empty string")
        else:
            name = name.strip()
            folded = name.casefold()
            if folded in seen_names:
                errors.append(f"{prefix}.name: duplicate label name {name!r}")
            else:
                seen_names.add(folded)

        if not isinstance(color, str) or COLOR_RE.fullmatch(color) is None:
            errors.append(
                f"{prefix}.color: must be exactly six hexadecimal characters without '#': {color!r}"
            )

        if description is None:
            description = ""
        if not isinstance(description, str):
            errors.append(f"{prefix}.description: must be a string or null")
        elif len(description) > 100:
            errors.append(f"{prefix}.description: must not exceed 100 characters")

        if (
            isinstance(name, str)
            and name.strip()
            and isinstance(color, str)
            and COLOR_RE.fullmatch(color)
            and isinstance(description, str)
            and len(description) <= 100
        ):
            labels.append(
                LabelDefinition(
                    name=name.strip(),
                    color=color.lower(),
                    description=description,
                )
            )

    if errors:
        raise ConfigError("Invalid label configuration:\n- " + "\n- ".join(errors))

    return labels


def needs_update(existing: dict[str, Any], desired: LabelDefinition) -> bool:
    existing_name = str(existing.get("name", ""))
    existing_color = str(existing.get("color", "")).lower()
    existing_description = existing.get("description") or ""
    return (
        existing_name != desired.name
        or existing_color != desired.color
        or existing_description != desired.description
    )


def sync_repository(
    client: GitHubClient,
    full_name: str,
    desired_labels: Iterable[LabelDefinition],
    *,
    dry_run: bool,
) -> RepoStats:
    existing_labels = client.list_labels(full_name)
    existing_by_name: dict[str, dict[str, Any]] = {}
    for existing in existing_labels:
        name = existing.get("name")
        if isinstance(name, str):
            existing_by_name[name.casefold()] = existing

    desired = list(desired_labels)
    desired_names = {label.name.casefold() for label in desired}
    stats = RepoStats(
        kept=sum(
            1
            for existing in existing_labels
            if isinstance(existing.get("name"), str)
            and existing["name"].casefold() not in desired_names
        )
    )

    for label in desired:
        existing = existing_by_name.get(label.name.casefold())
        if existing is None:
            LOGGER.info("%s CREATE %s%s", full_name, label.name, " [dry-run]" if dry_run else "")
            if not dry_run:
                client.create_label(full_name, label)
            stats.created += 1
            continue

        if needs_update(existing, label):
            LOGGER.info("%s UPDATE %s%s", full_name, label.name, " [dry-run]" if dry_run else "")
            if not dry_run:
                client.update_label(full_name, str(existing["name"]), label)
            stats.updated += 1
        else:
            stats.unchanged += 1

    return stats


def run(client: GitHubClient, labels: list[LabelDefinition], *, dry_run: bool) -> RunStats:
    repositories = client.list_installation_repositories()
    stats = RunStats()

    for repository in repositories:
        full_name = repository.get("full_name")
        if not isinstance(full_name, str) or not full_name:
            LOGGER.error("Skipping repository with missing full_name")
            stats.repositories_failed += 1
            continue

        if repository.get("archived") or repository.get("disabled"):
            LOGGER.info("%s SKIP archived/disabled", full_name)
            stats.repositories_skipped += 1
            continue

        try:
            repo_stats = sync_repository(client, full_name, labels, dry_run=dry_run)
        except (GitHubAPIError, ValueError) as exc:
            LOGGER.error("%s FAILED: %s", full_name, exc)
            stats.repositories_failed += 1
            continue

        stats.add_repo(repo_stats)
        LOGGER.info(
            "%s OK create=%d update=%d noop=%d keep=%d",
            full_name,
            repo_stats.created,
            repo_stats.updated,
            repo_stats.unchanged,
            repo_stats.kept,
        )

    return stats


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(".github/labels.yml"),
        help="Path to canonical labels YAML",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and log changes without issuing write requests",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv or sys.argv[1:])

    try:
        labels = load_config(args.config)
    except ConfigError as exc:
        LOGGER.error("Configuration validation failed: %s", exc)
        return 2

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        LOGGER.error("GITHUB_TOKEN is required")
        return 2

    api_url = os.environ.get("GITHUB_API_URL", DEFAULT_API_URL)
    client = GitHubClient(token, api_url)

    try:
        stats = run(client, labels, dry_run=args.dry_run)
    except (GitHubAPIError, ValueError) as exc:
        LOGGER.error("Global synchronization failure: %s", exc)
        return 2

    LOGGER.info(
        "SUMMARY repositories: success=%d failed=%d skipped=%d; labels: create=%d update=%d noop=%d keep=%d; dry_run=%s",
        stats.repositories_succeeded,
        stats.repositories_failed,
        stats.repositories_skipped,
        stats.created,
        stats.updated,
        stats.unchanged,
        stats.kept,
        str(args.dry_run).lower(),
    )

    return 1 if stats.repositories_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
