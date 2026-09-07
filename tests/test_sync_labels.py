from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from scripts.sync_labels import (
    ConfigError,
    GitHubAPIError,
    GitHubClient,
    LabelDefinition,
    load_config,
    run,
    sync_repository,
)


class FakeClient:
    def __init__(
        self,
        *,
        repositories: list[dict[str, Any]] | None = None,
        labels_by_repo: dict[str, list[dict[str, Any]]] | None = None,
        failing_repos: set[str] | None = None,
    ) -> None:
        self.repositories = repositories or []
        self.labels_by_repo = labels_by_repo or {}
        self.failing_repos = failing_repos or set()
        self.created: list[tuple[str, LabelDefinition]] = []
        self.updated: list[tuple[str, str, LabelDefinition]] = []

    def list_installation_repositories(self) -> list[dict[str, Any]]:
        return self.repositories

    def list_labels(self, full_name: str) -> list[dict[str, Any]]:
        if full_name in self.failing_repos:
            raise GitHubAPIError("boom")
        return list(self.labels_by_repo.get(full_name, []))

    def create_label(self, full_name: str, label: LabelDefinition) -> None:
        self.created.append((full_name, label))

    def update_label(self, full_name: str, current_name: str, label: LabelDefinition) -> None:
        self.updated.append((full_name, current_name, label))


class RecordingGitHubClient(GitHubClient):
    def __init__(self, responses: list[Any]) -> None:
        super().__init__("test-token")
        self.responses = list(responses)
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def request(self, method: str, path: str, *, query=None, payload=None):
        self.calls.append((method, path, query))
        if not self.responses:
            raise AssertionError("Unexpected request")
        return self.responses.pop(0), {}


class ConfigTests(unittest.TestCase):
    def write_config(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        tmp.write(content)
        tmp.close()
        return Path(tmp.name)

    def test_load_valid_config(self) -> None:
        path = self.write_config(
            """\
version: 1
labels:
  - name: 'type: bug'
    color: D73A4A
    description: Bug
"""
        )
        self.assertEqual(
            load_config(path),
            [LabelDefinition("type: bug", "d73a4a", "Bug")],
        )

    def test_rejects_invalid_color(self) -> None:
        path = self.write_config(
            """\
version: 1
labels:
  - name: bug
    color: '#ffffff'
"""
        )
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_rejects_long_description(self) -> None:
        path = self.write_config(
            "version: 1\nlabels:\n  - name: bug\n    color: ffffff\n    description: '"
            + ("x" * 101)
            + "'\n"
        )
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_rejects_case_insensitive_duplicate_names(self) -> None:
        path = self.write_config(
            """\
version: 1
labels:
  - name: Bug
    color: ffffff
  - name: bug
    color: 000000
"""
        )
        with self.assertRaises(ConfigError):
            load_config(path)


class SyncTests(unittest.TestCase):
    def test_create_update_noop_and_keep(self) -> None:
        client = FakeClient(
            labels_by_repo={
                "yohi/repo": [
                    {"name": "Type: Bug", "color": "ffffff", "description": "old"},
                    {"name": "status: ready", "color": "123456", "description": "Ready"},
                    {"name": "local", "color": "999999", "description": "Local"},
                ]
            }
        )
        desired = [
            LabelDefinition("type: bug", "d73a4a", "Bug"),
            LabelDefinition("status: ready", "123456", "Ready"),
            LabelDefinition("type: enhancement", "a2eeef", "Enhancement"),
        ]

        stats = sync_repository(client, "yohi/repo", desired, dry_run=False)

        self.assertEqual(stats.created, 1)
        self.assertEqual(stats.updated, 1)
        self.assertEqual(stats.unchanged, 1)
        self.assertEqual(stats.kept, 1)
        self.assertEqual(client.created[0][1].name, "type: enhancement")
        self.assertEqual(client.updated[0][1], "Type: Bug")
        self.assertEqual(client.updated[0][2].name, "type: bug")

    def test_dry_run_never_writes(self) -> None:
        client = FakeClient(labels_by_repo={"yohi/repo": []})
        stats = sync_repository(
            client,
            "yohi/repo",
            [LabelDefinition("bug", "ffffff")],
            dry_run=True,
        )
        self.assertEqual(stats.created, 1)
        self.assertEqual(client.created, [])
        self.assertEqual(client.updated, [])

    def test_partial_failure_continues_and_marks_failure(self) -> None:
        client = FakeClient(
            repositories=[
                {"full_name": "yohi/a", "archived": False, "disabled": False},
                {"full_name": "yohi/b", "archived": False, "disabled": False},
                {"full_name": "yohi/c", "archived": False, "disabled": False},
                {"full_name": "yohi/d", "archived": True, "disabled": False},
            ],
            failing_repos={"yohi/b"},
        )
        stats = run(client, [], dry_run=False)
        self.assertEqual(stats.repositories_succeeded, 2)
        self.assertEqual(stats.repositories_failed, 1)
        self.assertEqual(stats.repositories_skipped, 1)


class PaginationTests(unittest.TestCase):
    def test_repository_pagination(self) -> None:
        first = [{"full_name": f"yohi/repo-{i}"} for i in range(100)]
        second = [{"full_name": "yohi/repo-100"}]
        client = RecordingGitHubClient(
            [
                {"repositories": first},
                {"repositories": second},
            ]
        )
        repos = client.list_installation_repositories()
        self.assertEqual(len(repos), 101)
        self.assertEqual(client.calls[0][2]["page"], 1)
        self.assertEqual(client.calls[1][2]["page"], 2)

    def test_label_pagination(self) -> None:
        first = [{"name": f"label-{i}"} for i in range(100)]
        second = [{"name": "label-100"}]
        client = RecordingGitHubClient([first, second])
        labels = client.list_labels("yohi/repo")
        self.assertEqual(len(labels), 101)
        self.assertEqual(client.calls[0][2]["page"], 1)
        self.assertEqual(client.calls[1][2]["page"], 2)


if __name__ == "__main__":
    unittest.main()
