# .github

`yohi` 配下の全リポジトリに対する GitHub 共通設定・再利用ワークフローを管理するリポジトリ。

## 含まれるワークフロー

| ワークフロー | 説明 |
|---|---|
| [`ocr-review.yml`](./.github/workflows/ocr-review.yml) | OpenCodeReview を実行する **Reusable Workflow** (workflow_call) |
| [`caller-example.yml`](./.github/workflows/caller-example.yml) | dotfiles などの各リポジトリに配置する呼び出し側サンプル |
| [`sync-labels.yml`](./.github/workflows/sync-labels.yml) | GitHub App を使い、共通ラベル定義を `yohi/*` の対象リポジトリへ同期 |

## ドキュメント

- [Documentation Architecture Standard](./docs/documentation-architecture.md) / [日本語](./docs/documentation-architecture.ja.md) — `yohi/*` における README、SPEC、AGENTS、`docs/` の責務、命名、言語、SSOT の共通標準
- [Repository Label Sync](./docs/repository-label-sync.md) — GitHub App の権限、Secrets/Variables、同期ルール、dry-run、障害時の挙動
- [OpenCodeReview GitHub Actions セットアップガイド](./docs/OPEN_CODE_REVIEW_SETUP.md) — 呼び出し側の Secrets 設定、Reusable Workflow の `with:` パラメータ、トラブルシューティングなど
