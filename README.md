# .github

`yohi` 配下の全リポジトリに対する GitHub 共通設定・再利用ワークフローを管理するリポジトリ。

## 含まれるワークフロー

| ワークフロー | 説明 |
|---|---|
| [`ocr-review.yml`](./.github/workflows/ocr-review.yml) | OpenCodeReview を実行する **Reusable Workflow** (workflow_call) |
| [`caller-example.yml`](./.github/workflows/caller-example.yml) | dotfiles などの各リポジトリに配置する呼び出し側サンプル |

## ドキュメント

- [OpenCodeReview GitHub Actions セットアップガイド](./docs/OPEN_CODE_REVIEW_SETUP.md) — 呼び出し側の Secrets 設定、Reusable Workflow の `with:` パラメータ、トラブルシューティングなど

