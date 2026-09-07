# `yohi/*` ドキュメントアーキテクチャ標準

[English](documentation-architecture.md)

> [!NOTE]
> この文書は [English version](documentation-architecture.md) の日本語訳です。内容に差異がある場合は英語版を正とします。

この標準は、`yohi/*` 配下のリポジトリにおけるドキュメントの責務、配置、命名、言語、正本関係、品質基準を統一するためのものです。

基本思想は次のとおりです。

> 情報の正本を明確にし、読者ごとに適切な入口を提供し、同じ情報を複数箇所で重複管理しない。

## 1. 目的

この標準では、特に以下を重視します。

- Human-facing documentation と Agent-facing documentation を分離する。
- README を discovery / onboarding に集中させる。
- README を仕様書、Runbook、Agent playbook の正本にしない。
- English を canonical language とする。
- Japanese は必要な human-facing documentation の翻訳として提供する。
- normative / machine-consumed documentation は単一正本を維持する。
- repository-level canonical document と topic-specific document を命名規則で区別する。
- user / contributor / operator / AI agent が適切な情報へ短距離で到達できるようにする。

## 2. 基本構成

成熟したリポジトリでは、必要に応じて概ね以下の構成を採用します。

```text
repository/
├── README.md
├── README.ja.md
│
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CONTRIBUTING.ja.md
├── SECURITY.md
├── LICENSE
│
├── AGENTS.md
├── SPEC.md
│
└── docs/
    ├── architecture.md
    ├── architecture.ja.md
    ├── configuration.md
    ├── configuration.ja.md
    ├── deployment.md
    ├── deployment.ja.md
    ├── operations.md
    ├── operations.ja.md
    ├── migration.md
    ├── migration.ja.md
    └── ...
```

すべてのリポジトリにすべてのファイルを作成する必要はありません。実際に責務が存在する文書だけを作成します。

## 3. 責務モデル

各ドキュメントの主責務を明確に分離します。

```text
README
  -> Discovery / Onboarding / Routing

SPEC
  -> Correctness / Normative Technical Specification

AGENTS
  -> AI Agent Behavior / Repository-specific Instructions
docs/*
  -> Human-oriented Detailed Documentation

CHANGELOG
  -> Release History

CONTRIBUTING
  -> Human Contribution Workflow

SECURITY
  -> Security Policy
```

最重要原則は次のとおりです。

> 同じ情報について複数の canonical source を作らない。

## 4. README.md

### 役割

`README.md` はプロジェクトの入口です。主に以下の3つを担います。

1. Project Landing Page
2. Quick Start
3. Documentation Router

README は完全な技術仕様書ではありません。

### README に置く情報

必要に応じて以下を配置します。

- Project name
- One-line value proposition
- What / Why
- Status / Important notice
- Badges
- Quick Start
- Main features
- Representative usage
- High-level architecture
- 最重要 configuration のみ
- 詳細ドキュメントへのリンク
- 基本的な development instructions

### README を正本にしない情報

以下は専用文書へ分離します。

- 完全な architecture specification
- HTTP contract
- MCP tool reference
- 完全な configuration reference
- Environment variable catalog
- Deployment runbook
- Operations runbook
- Migration manual
- 網羅的 troubleshooting catalog
- AI Agent playbook

README には要約とリンクのみを置きます。

## 5. Canonical README Structure

標準構成は以下です。

```text
# Project Name

Language switch

Badges

One-line value proposition
Short What / Why

Important status notice

## Quick Start

## Features

## How It Works

## Usage

## Configuration

## Documentation

## Development

## Deployment        optional
## Operations        optional
## Migration         optional

## License
```

不要なセクションは空のまま残さず省略します。

## 6. Reader Journey

README の順序は実装内部ではなく、読者の疑問順にします。

```text
これは何か？
      ↓
なぜ必要か？
      ↓
自分に関係があるか？
      ↓
どう試すか？
      ↓
どう使うか？
      ↓
どう動いているか？
      ↓
詳細はどこか？
```

そのため、原則として以下をREADME冒頭に置きません。

- Repository layout
- Internal modules
- Storage internals
- 完全な environment variable list
- Migration detail
- Release procedure
- Agent tool-selection rule

## 7. Quick Start

Quick Start の目的は、初見ユーザーを最小手順で最初の成功状態まで導くことです。

通常は以下だけを含めます。

1. 最小要件
2. Installation
3. Minimal configuration
4. 1つの実行経路
5. Expected result / success condition

Quick Start を完全な installation / deployment / migration / troubleshooting manual にしません。

原則として明確な Quick Start は1つにします。開発用サンドボックス等の特殊な開発フローは `Development` または専用ガイドへ置きます。

## 8. Reader Routing

明確に異なる読者が存在する場合は、入口を分けます。

```markdown
## Get Started

| I want to... | Start here |
| --- | --- |
| Use the service | [Quick Start](#quick-start) |
| Develop locally | [Development](#development) |
| Deploy my own instance | [Deployment](docs/deployment.md) |
| Configure an AI agent | [Agent Instructions](AGENTS.md) |
```

主な reader role は以下です。

- user
- developer
- operator
- AI agent

Routing 自体は短く保ち、完全な手順はリンク先に置きます。

## 9. Badges

Badge は装飾ではなく status indicator として扱います。

意味のある2〜5個程度を目安にします。

推奨順序:

```text
CI
→ CodeRabbit
→ Release
→ Runtime / Protocol / Ecosystem
→ License
```

推奨カテゴリ:

- CI / Tests
- CodeRabbit PR Reviews
- Release / Version
- Runtime / Language
- Protocol
- Package registry
- License

Stars、Forks、Repo size、Code size、Issue count、PR count 等の vanity badge を大量に並べることは避けます。

## 10. SPEC.md

### 役割

`SPEC.md` は implementation correctness のための normative technical source of truth です。

Human と AI Agent の双方が参照できますが、tutorial 的な読みやすさよりも precision を優先します。

### 主な内容

- Detailed architecture
- Design invariants
- State transitions
- Failure semantics
- Protocol behavior
- HTTP contracts
- Request / response rules
- Data consistency rules
- Security guarantees
- Compatibility guarantees
- Acceptance criteria

### 翻訳

`SPEC.md` は English only とします。

```text
SPEC.md
SPEC.ja.md   <- 作らない
```

日本語でarchitectureの説明が必要な場合は、normative spec を複製せず `docs/architecture.ja.md` 等の human-oriented document を作成します。

## 11. AGENTS.md

### 役割

`AGENTS.md` は repository-specific AI agent instruction の正本です。

### 主な内容

- Mandatory constraints
- Allowed / forbidden behavior
- Tool selection rules
- Verification requirements
- Repository-specific workflows
- Test requirements
- Context loading policy
- Generated-file rules
- Safety constraints
- Implementation conventions

### 翻訳

`AGENTS.md` も English only とします。

```text
AGENTS.md
AGENTS.ja.md   <- 作らない
```

README に完全な Agent playbook を複製しません。README には短いroutingのみ置きます。

例:

```text
For automated setup, ask your coding agent to follow AGENTS.md.
```

## 12. Human-facing docs/

`docs/` には、人間が理解・操作するための詳細文書を置きます。

```text
docs/
├── architecture.md
├── configuration.md
├── deployment.md
├── operations.md
├── migration.md
├── troubleshooting.md
├── getting-started.md
└── ...
```

### architecture.md

Human-oriented architecture explanation。`SPEC.md` より comprehension と context を優先し、正確な挙動が必要な箇所では `SPEC.md` へリンクします。

### configuration.md

完全な configuration reference を置きます。

- settings / environment variables
- defaults
- required / optional
- examples
- security implications

### deployment.md

必要に応じて以下を扱います。

- setup
- secrets
- CI/CD
- production deployment
- verification

### operations.md

必要に応じて以下を扱います。

- monitoring
- alerting
- recovery
- rollback
- incident handling
- quota handling

### migration.md

version migration procedure の正本です。README では breaking change の存在を短く示し、実際の手順はここへ誘導します。

## 13. Language Policy

### Canonical language

`yohi/*` の documentation は English を canonical language とします。

```text
README.md
docs/architecture.md
docs/configuration.md
```

### Japanese localization

人間が読むことを主目的とする文書のみ、必要に応じて日本語化します。

命名規則:

```text
<name>.md
<name>.ja.md
```

例:

```text
README.md
README.ja.md

docs/architecture.md
docs/architecture.ja.md
```

`README.en.md` を正本にせず、GitHub がデフォルト表示する `README.md` 自体を English canonical とします。

## 14. Translation Scope

### 原則として日本語化を検討するもの

- README
- Getting Started
- Installation / Setup
- Main Usage documentation

### 必要性に応じて日本語化するもの

- Architecture
- Configuration
- Deployment
- Operations
- Migration
- Contributing
- Troubleshooting

翻訳価値が保守コストを上回る場合に作成します。

### 翻訳しないもの

- `AGENTS.md`
- `SPEC.md`
- schemas
- skills
- prompts
- machine-consumed configuration
- generated documentation
- normative protocol definitions

## 15. Translation SSOT

English と Japanese を2つの独立した正本にしません。

関係は常に以下です。

```text
English canonical
       ↓
Japanese translation
```

正しい更新フロー:

```text
README.md
   ↓ update
README.ja.md
   ↓ synchronize translation
```

日本語版で factual problem が見つかった場合も、English canonical を先に修正し、その後日本語版を同期します。

日本語版には以下のような注記を置けます。

```markdown
> [!NOTE]
> この文書は [English version](README.md) の日本語訳です。
> 内容に差異がある場合は英語版を正とします。
```

## 16. Language Switch

Human-facing localized document の冒頭付近に、反対言語へのリンクを置きます。

English README:

```markdown
[日本語](README.ja.md)
```

Japanese README:

```markdown
[English](README.md)
```

現在のページ自身へのリンクは不要です。

## 17. File Naming Convention

### Repository-level canonical documents

リポジトリ全体に特別な意味を持つ文書は uppercase filename とします。

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
CODE_OF_CONDUCT.md
SUPPORT.md
AGENTS.md
SPEC.md
LICENSE
```

### Topic-specific documentation

`docs/` 配下は lowercase kebab-case とします。

```text
docs/architecture.md
docs/configuration.md
docs/agent-setup.md
docs/http-contract.md
docs/routing-weights-rationale.md
docs/cloudflare-ai-gateway-custom-provider.md
```

日本語版は `.ja.md` を使用します。

```text
docs/architecture.ja.md
docs/agent-setup.ja.md
```

基本ルール:

> Repository-level canonical documents use uppercase filenames. Topic-specific human documentation uses lowercase kebab-case.

## 18. CHANGELOG.md

`CHANGELOG.md` は原則 English only とします。

理由:

- release tooling と整合しやすい
- release title / commit / PR と同一言語で管理しやすい
- 2言語のrelease historyは同期コストが高い
- historical record は1つの正本で十分

```text
CHANGELOG.md
CHANGELOG.ja.md   <- 原則作らない
```

## 19. CONTRIBUTING.md

`CONTRIBUTING.md` は human-facing なので、必要に応じて日本語版を作成できます。

```text
CONTRIBUTING.md
CONTRIBUTING.ja.md
```

外部contributionを積極的に受け付けない小規模repoではEnglish onlyでも構いません。

## 20. SECURITY.md

`SECURITY.md` は human-facing ですが、重要情報の二重管理リスクがあります。

標準では English only で問題ありません。

日本語でのsecurity reportを想定する場合は `SECURITY.ja.md` を追加できますが、supported versions や reporting contacts は必ず同期します。

## 21. Single Source of Truth Matrix

| Information | Canonical source | Japanese localization |
| --- | --- | --- |
| Project overview | `README.md` | `README.ja.md` |
| Quick Start | `README.md` | `README.ja.md` |
| Main features | `README.md` | `README.ja.md` |
| High-level architecture | `README.md` | `README.ja.md` |
| Detailed architecture | `SPEC.md` | Human explanation only |
| Design invariants | `SPEC.md` | No |
| Protocol contract | `SPEC.md` または専用 normative reference | No |
| MCP tool contract | Normative technical reference | No |
| Agent behavior | `AGENTS.md` | No |
| Configuration reference | `docs/configuration.md` | Optional |
| Deployment | `docs/deployment.md` | Optional |
| Operations | `docs/operations.md` | Optional |
| Migration | `docs/migration.md` | Optional |
| Contribution guide | `CONTRIBUTING.md` | Optional |
| Release history | `CHANGELOG.md` | No |
| Security policy | `SECURITY.md` | Optional |

## 22. Information Flow

理想的な導線は以下です。

```text
GitHub visitor
     │
     ▼
README.md
     │
     ├── Quick Start
     │
     ├── Usage
     │
     ├── Architecture Overview
     │
     └── Documentation Index
            │
            ├── docs/*
            │      Human detailed documentation
            │
            ├── SPEC.md
            │      Normative technical truth
            │
            └── AGENTS.md
                   Agent behavioral truth
```

日本語利用者の場合:

```text
README.md
   │
   └── README.ja.md
           │
           ├── docs/*.ja.md
           └── normative technical documents
                  ↓
              English only
```

## 23. Duplication Rules

### Agent instructions

README、`AGENTS.md`、Skill に同じAgent ruleをコピーしません。

正本を1つ決め、他からそこへroutingします。

### Specification

同じprotocol contractをREADME、`SPEC.md`、`docs/http-contract.md` で独立管理しません。

1つの文書がcontractを所有し、他は要約とリンクにします。

### Configuration

README、`.env.example`、`docs/configuration.md` で同じ設定表を独立管理しません。

推奨責務分離:

```text
.env.example
    -> machine-usable input template

docs/configuration.md
    -> human explanation and complete reference

README
    -> only the most important settings and routing
```

## 24. Repository Archetypes

すべてのrepoに同一READMEテンプレートを強制しません。共通原則を維持しながら、project typeごとに適切なarchetypeを使います。

### Type A: Library / Plugin

例: `justice`, `akane`

```text
README
├── Quick Start
├── Features
├── Usage
├── Configuration
├── How It Works
└── Development
```

### Type B: AI Agent / MCP Product

例: `nexus`, `chronos-graph`

```text
README
├── Quick Start
├── Features
├── Agent Setup
├── Usage
├── How It Works
├── Documentation
└── Development

AGENTS.md
└── complete agent rules
```

### Type C: Gateway / Service / Infrastructure

例: `octg`, `opencode-cloudflare-ai-gateway-chatgpt`, `ocr-app`

```text
README
├── Get Started
├── Quick Start
├── Features
├── Architecture Overview
├── Usage
├── Configuration Summary
└── Documentation

SPEC / docs
├── protocol
├── deployment
└── operations
```

### Type D: Configuration / Operations Repository

例: `cf-ai-gw-dynamic-routing`, `dotfiles-ai`

end user が直接install/runしないrepoでは、無理にQuick Startを置かず、以下を利用できます。

```text
## How to Use This Repository
```

## 25. README Size Guidance

行数そのものを品質指標にはしませんが、警告シグナルとして利用できます。

目安:

- 約100〜300行: 多くのlibrary / pluginで健全
- 300〜500行: 詳細情報の外出しを検討
- 500行超: specification / reference / runbook / migration / full agent instruction が混在していないか強く確認

長いREADME自体を禁止しません。入口に置く価値がある情報かどうかで判断します。

## 26. Quality Gates

### README first-screen test

冒頭だけで以下が分かること。

- [ ] 何のprojectか
- [ ] なぜ存在するか
- [ ] 誰向けか
- [ ] Status / Breaking Change があるか
- [ ] CI / release state はどうか

### Quick Start test

初見ユーザーが短時間で少なくとも以下のいずれかを達成できること。

- [ ] install
- [ ] run
- [ ] API call
- [ ] client configuration
- [ ] AI agentへのsetup委譲
- [ ] repoの正しい使い方の理解

### SSOT test

- [ ] Agent rules が重複していない
- [ ] Protocol definition の正本が1つ
- [ ] Configuration reference の正本が1つ
- [ ] Migration procedure の正本が1つ
- [ ] Japanese は English から派生している

### Structure test

- [ ] H1は1つ
- [ ] Heading hierarchyが意味的に正しい
- [ ] 対応するH2より前にH3が出ない
- [ ] 見出しだけで文書構造を把握できる
- [ ] Architectureそのものがproduct理解に不可欠な場合を除き、Quick Startが深い実装詳細より前にある

### Naming test

- [ ] repository-level canonical documents は uppercase
- [ ] `docs/` は lowercase kebab-case
- [ ] Japanese は `.ja.md`

### Localization test

- [ ] Human-facing documentation のみ翻訳
- [ ] English が canonical
- [ ] Japanese は derived translation
- [ ] `AGENTS.md` を翻訳していない
- [ ] `SPEC.md` を翻訳していない
- [ ] Japanese-only factual change を独立管理していない

## 27. Canonical Summary

このアーキテクチャは以下のように要約できます。

```text
README
    = onboarding

SPEC
    = technical correctness

AGENTS
    = agent behavior
docs
    = human detailed documentation

English
    = canonical

Japanese
    = human-facing localization
```

命名も同じ思想に従います。

Repository-level canonical documents:

```text
README.md
SPEC.md
AGENTS.md
CHANGELOG.md
```

Topic-specific human documentation:

```text
docs/architecture.md
docs/configuration.md
docs/deployment.md
```

Japanese localization:

```text
README.ja.md
docs/architecture.ja.md
```

## 28. Governing Principles

1. **READMEは入口であり、仕様書ではない。**
2. **SPECは技術的正しさの正本とする。**
3. **AGENTSはAI Agent行動規範の正本とする。**
4. **詳細な人間向け説明は `docs/` に置く。**
5. **同じ情報の正本を複数作らない。**
6. **Englishをcanonical languageとする。**
7. **Japanese localizationはhuman-facing documentationのみに限定する。**
8. **Agent-facing / normative technical documentsは翻訳しない。**
9. **repository-level canonical documentsはuppercase、topic-specific docsはlowercase kebab-caseとする。**
10. **ドキュメント品質は、1ファイルにどれだけ情報を詰めたかではなく、対象読者が正しい情報へどれだけ速く到達できるかで評価する。**