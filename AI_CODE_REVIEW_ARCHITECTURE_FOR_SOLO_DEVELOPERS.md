# AI Code Review Architecture for Solo Developers

## 1. 概要 (Executive Summary)

本アーキテクチャは、個人開発者が「シニアエンジニア級のコードレビュー」を低コスト（実質無料〜数ドル/月）で享受するためのハイブリッドAIシステムです。

**「漏斗（Funnel）戦略」**を採用し、コストのかからない順にフィルターを通過させることで、SaaSのトークン消費を最小限に抑えつつ、致命的なバグやセキュリティリスクを排除します。

### Architecture Diagram

```mermaid
graph TD
    User((Developer)) -->|Commit Code| Local[Local Environment]

    subgraph "Phase 0: The Iron Gate (Security & Lint)"
        direction TB
        Local -->|Husky| Gitleaks[Gitleaks (Secret Scan)]
        Gitleaks -->|Pass| Linter[Lint-staged (Format/Static)]
        Linter -- Error/Leak --> User
        Linter -- Pass --> Github[GitHub Repo (Public)]
    end

    subgraph "Phase 1: The Reviewer (Routine Check)"
        Github -->|PR Open/Update| CR[CodeRabbit (Lite)]
        CR -->|Logic & Readability| PR_Com[PR Comments]
        PR_Com -.->|Fix| User
    end

    subgraph "Phase 2: The Auditor (Deep Scan)"
        User -->|Label: audit-required| Github
        Github -->|Action Trigger| Grep[Greptile (OSS Free)]
        Grep -->|Arch, Security, DB| PR_Com_Deep[Deep Audit]
        PR_Com_Deep -.->|Refactor| User
    end

    User -->|Approve| Merge[Main Branch]
```

---

## 2. 戦略と役割分担 (Strategy)

| Phase | Tool | Role | Cost / Plan | Trigger |
| --- | --- | --- | --- | --- |
| **0. Iron Gate** | **Husky + Gitleaks** | **防壁**<br>機密情報の流出阻止、スタイル統一。<br>Publicリポジトリ運用の生命線。 | **無料**<br>Local Resource | **Commit時**<br>(強制ブロック) |
| **1. Reviewer** | **CodeRabbit** | **ペアプログラマー**<br>可読性、単純バグ、保守性のチェック。<br>「人格」を排し、事実のみを指摘させる。 | **安価**<br>Lite Plan<br>(Chat OFF) | **PR作成/更新**<br>(自動) |
| **2. Auditor** | **Greptile** | **外部監査役**<br>複雑なロジック、仕様バグ、セキュリティ。<br>ここぞという時のみ召喚する。 | **無料**<br>OSS Free枠<br>(API制限あり) | **Label付与**<br>(手動判断) |

---

## 3. リポジトリ構成 (Repository Structure)

```text
[github.com/username/](https://github.com/username/)
├── .github/                        # [Central Repo] 設定集約用
│   └── .github/
│       └── coderabbit.yaml         # CodeRabbit共通設定（厳格モード）
│
└── <project-repo>/                 # [Local Repo] 個別プロジェクト
    ├── greptile.json               # Greptile設定（プロジェクト固有）
    ├── .husky/                      # Pre-commitフック
    │   └── pre-commit              # Gitleaks & Lint 実行スクリプト
    ├── .github/
    │   └── workflows/
    │       └── trigger-greptile.yml # 監査トリガー
    └── src/
```

---

## 4. 実装詳細 (Implementation)

### A. Phase 0: The Iron Gate (Husky + Gitleaks)

Publicリポジトリ運用における「事故」を物理的に防ぎます。

**前提:** `gitleaks` のインストール (`brew install gitleaks` 等) が必要です。

**File:** `.husky/pre-commit`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# 1. Security Scan (Secret Detection)
# ステージングされたファイルからAPIキーやトークンを検出したらコミットを即ブロック
if command -v gitleaks >/dev/null 2>&1; then
    echo "🔒 Running Gitleaks..."
    gitleaks protect --staged --verbose
    if [ $? -ne 0 ]; then
        echo "❌ Gitleaks detected secrets! Commit aborted."
        exit 1
    fi
else
    echo "⚠️ Gitleaks not found. Skipping secret scan."
fi

# 2. Static Analysis & Formatting
echo "✨ Running Lint-staged..."
npx lint-staged
```

### B. Phase 1: CodeRabbit (Strict Mode)

Liteプランの制限内で最大の効果を得るため、AIに「感情」と「お世辞」を禁じます。

**File:** `<username>/.github/.github/coderabbit.yaml`

```yaml
reviews:
  profile: "chill"
  request_changes_workflow: false
  high_level_summary: false  # トークン節約＆自分には不要なためOFF
  auto_review:
    enabled: true
    drafts: false
    ignore_title_keywords: ["WIP", "Do not review", "Draft"]
  path_filters:
    - "!**/dist/**"
    - "!**/build/**"
    - "!**/*.lock"
    - "!**/generated/**"
    - "!**/public/assets/**"

  # ソロ開発特化・厳格プロンプト
  instructions: |
    あなたはソロ開発者を支援する、冷徹で論理的な「コード監査官」です。

    # 🚫 禁止事項（トークンの無駄です）
    - 肯定的な感想 (例: "Great work", "LGTM")
    - 挨拶や前置き (例: "I reviewed your code...")
    - Linter/Formatterで検知可能な些末なスタイル指摘
    - ドキュメントコメントの不足指摘

    # 🔍 重点監査項目
    1. **バグとエッジケース**: Null/Undefined、境界値、例外処理の漏れ
    2. **パフォーマンス**: N+1問題、無駄な再レンダリング、重いループ
    3. **型安全性**: `any` の使用、型推論への過度な依存、型定義の不整合
    4. **セキュリティ**: XSS、Injection、不適切な権限管理（Phase 0漏れの最終防衛）

    # 📝 出力形式
    - 指摘は簡潔な日本語で箇条書きにしてください。
    - 修正案は `diff` ではなく、コピー可能なコードブロックで提示してください。

chat:
  auto_reply: false  # Liteプランのためチャット無効化
```

### C. Phase 2: Greptile (Optimization)

OSS無料枠の制限とレスポンス時間を考慮し、コンテキストサイズを極限まで絞ります。

**File:** `<project-repo>/greptile.json`

```json
{
    "skipReview": "AUTOMATIC",
    "commentTypes": ["logic", "security", "performance", "design"],
    "strictness": 4,
    "triggerOnUpdates": false,
    "ignorePatterns": [
        "**/package-lock.json",
        "**/yarn.lock",
        "**/pnpm-lock.yaml",
        "**/dist/**",
        "**/*.min.js",
        "**/public/assets/**",
        "**/test/fixtures/**",
        "**/__mocks__/**",
        "**/*.md"
    ]
}
```

### D. Trigger Workflow (GitHub Actions)

**File:** `<project-repo>/.github/workflows/trigger-greptile.yml`

```yaml
name: Trigger Greptile Audit
on:
  pull_request:
    types: [labeled]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  trigger-greptile:
    if: github.event.label.name == 'audit-required'
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Greptile and Reset Label
        uses: actions/github-script@v7
        with:
          # Note: Must use a Fine-grained PAT, not GITHUB_TOKEN
          github-token: ${{ secrets.PAT_FOR_TRIGGER }}
          script: |
            const prNumber = context.payload.pull_request.number;
            const owner = context.repo.owner;
            const repo = context.repo.repo;

            try {
              console.log(`🔍 Triggering Greptile Audit for PR #${prNumber}...`);

              // 1. Trigger Greptile (コマンド発行)
              await github.rest.issues.createComment({
                owner,
                repo,
                issue_number: prNumber,
                body: '@greptileai review --ignore-comments'
              });

              // 2. Remove Label (即座に剥がして状態をリセット)
              await github.rest.issues.removeLabel({
                owner,
                repo,
                issue_number: prNumber,
                name: 'audit-required'
              });

            } catch (error) {
              core.setFailed(`Action failed: ${error.message}`);
            }
```

---

## 5. 運用ワークフロー (Operational Workflow)

### Step 1: Coding & Safety Check (Phase 0)

* 機能実装を行い、コミットします。
* `git commit` 実行時、**Gitleaks** が秘密鍵の混入をスキャンし、**Lint-staged** がコード整形を行います。
* もしGitleaksがエラーを出した場合、コミットは拒否されます。`.env` ファイルなどがステージングされていないか確認してください。

### Step 2: Routine Review (Phase 1)

* GitHubへPushし、PRを作成します。
* **CodeRabbit** が自動的に反応し、バグや論理エラーのみを指摘します。
* ここでの修正はコミットを積むことで行います（チャットで反論しない）。

### Step 3: Human Judgment (The Gate)

* CodeRabbitの指摘が解消された状態で、自身の変更内容を見直します。
* **以下のいずれかに該当するか？**
* [ ] 認証・認可に関わる変更
* [ ] データベーススキーマの変更 (マイグレーション)
* [ ] 決済ロジックの変更
* [ ] 複雑なコアロジックの大幅な書き換え

* **NO:** そのままマージ（Squash Merge推奨）。
* **YES:** Step 4へ。

### Step 4: Deep Audit (Phase 2)

* PRのLabelsから `audit-required` を選択します。
* GitHub Actionsが起動し、Greptileへレビューをリクエストします（ラベルは自動で外れます）。
* 数分〜数十分後、Greptileからの深い洞察（セキュリティホールや設計ミス）がコメントされます。
* 指摘事項を修正し、再度コミットします。

### Step 5: Merge

* 全ての懸念が払拭されたらマージします。

---

## 6. トラブルシューティング

* **Greptileが反応しない:** OSS枠はリクエスト過多で遅延することがあります。急ぎの場合は手動でPRに `@greptileai review` とコメントしてください。
* **CodeRabbitがうるさい:** `coderabbit.yaml` の `strictness` を調整するか、プロンプトで無視する項目を追加してください。
* **Gitleaksの誤検知:** 本当に公開して良いトークン（テスト用など）の場合は、行末に `# gitleaks:allow` を追加して回避します。
