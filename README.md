# .github

このリポジトリは、Organization（またはアカウント）全体のデフォルト設定、コミュニティ健全性ドキュメント、および共通の GitHub Actions ワークフローを一元管理するための特別なリポジトリです。

---

## 共通 GitHub Actions ワークフロー

### 1. Reusable Release Please
`release-please` を使ったリリース処理を共通化するための再利用可能ワークフロー (Reusable Workflow) です。

* **ファイルパス**: `.github/workflows/release-please.yml`
* **使用可能な `inputs`**:
  * `release-type`: リリースのタイプ（例: `node`, `python`, `go`, `rust` など。デフォルト: `node`）
  * `package-name`: パッケージの名前（オプション）
* **使用可能な `secrets`**:
  * `token`: リリース作成権限を持つ GitHub トークン（指定しない場合は `github.token` が自動的に使用されます）

#### 個別リポジトリからの呼び出し方法
各個別リポジトリの `.github/workflows/release.yml` から以下のように呼び出して使用します。

```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  call-release:
    uses: yohi/.github/.github/workflows/release-please.yml@main
    with:
      release-type: 'node' # リポジトリの種類に合わせて変更
    secrets:
      token: ${{ secrets.GITHUB_TOKEN }}
```

---

## 新規リポジトリ作成時の自動ラベル生成システム

アカウント配下で新しくリポジトリが作成された際、GitHub App と Cloudflare Workers を使って、共通ラベル（`labels.yml`）を自動的に一括作成・登録する仕組みです。

### 構成ファイル
* **`labels.yml`**: 自動生成するラベルの定義ファイル（名前、カラー、説明）
* **`automation-worker/`**: Cloudflare Workers の中継プログラム

### 構築・設定方法

#### 1. Cloudflare Workers のデプロイ
1. `automation-worker` ディレクトリに移動し、依存関係をインストールします。
   ```bash
   cd automation-worker
   npm install
   ```
2. Cloudflare にログインし、デプロイします。
   ```bash
   npx wrangler deploy
   ```
3. デプロイ後に発行される Workers の URL（例: `https://github-auto-label-worker.xxxx.workers.dev`）を控えておきます。
4. Workers の設定画面（Settings > Variables）または `npx wrangler secret put GH_PAT` コマンドを使用し、他のリポジトリへの書き込み権限を持つ GitHub の個人用アクセストークン（PAT）を `GH_PAT` として登録します。

#### 2. 個人用の GitHub App の作成とインストール
個人アカウントでのリポジトリ作成イベントを検知するために、自分専用の GitHub App を作成します。

1. GitHub の **Settings > Developer Settings > GitHub Apps > New GitHub App** を開きます。
2. 以下のように設定します：
   * **GitHub App name**: `yohi-auto-labeler` (任意)
   * **Homepage URL**: 任意のURL (例: `https://github.com/yohi`)
   * **Webhook**: `Active` にチェック
   * **Webhook URL**: 上記でデプロイした Workers の URL
3. **Permissions**:
   * **Repository permissions**:
     * `Metadata`: **Read-only**
     * `Administration`: **Read-only**（リポジトリの作成イベントを購読するために必要）
     * `Repository projects` / `Issues` などではなく、ラベル作成のためには **`Issues: Read & write`** 権限が必要です。
4. **Subscribe to events**:
   * **Repository** にチェックを入れます（リポジトリ作成イベント `repository` を取得するため）。
5. アプリを作成したら、**Install App** メニューから、自分の個人アカウントへインストールします。

これにより、新規リポジトリが作成されると同時に自動的にラベルのセットアップが完了するようになります。
