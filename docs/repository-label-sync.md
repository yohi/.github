# Repository Label Sync

`yohi/.github` is the single source of truth for labels managed across repositories owned by `yohi`.
The controller runs only from this repository; target repositories do not need their own workflow or label configuration.

## Architecture

```text
.github/labels.yml
        |
        v
.github/workflows/sync-labels.yml
        |
        v
GitHub App installation token
        |
        v
GET /installation/repositories
        |
        v
scripts/sync_labels.py
        |
        +--> create missing labels
        +--> update drifted labels
        +--> leave repository-local labels unchanged
```

Archived or disabled repositories are skipped. Public, private, forked, and `.github` itself are otherwise eligible when the GitHub App installation can access them.

## GitHub App setup

Create a private GitHub App for the `yohi` account. A suggested name is `yohi-label-sync`.

Configure repository permissions as follows:

| Permission | Access |
|---|---|
| Metadata | Read-only (implicit) |
| Issues | Read and write |

Do not grant unrelated write permissions such as Contents, Actions, or Administration.

Install the App on the `yohi` account. Use **All repositories** when every current and future repository should participate. If a narrower scope is desired, restrict the installation itself rather than adding a second allow/deny list to the controller.

Generate a private key for the App, then configure these values in `yohi/.github`:

| GitHub Actions setting | Name | Value |
|---|---|---|
| Repository variable | `LABEL_SYNC_APP_CLIENT_ID` | GitHub App Client ID |
| Repository secret | `LABEL_SYNC_APP_PRIVATE_KEY` | Complete generated private key |

The private key must be stored only as a secret. Do not place it in files, workflow arguments, logs, artifacts, variables, or committed environment files.

The workflow generates a short-lived installation token with `actions/create-github-app-token@v3`. It explicitly sets the repository owner and requests only `Issues: write`, so the token can reach every repository in the App installation without inheriting unrelated App permissions.

## Canonical label file

The canonical configuration is `.github/labels.yml`:

```yaml
version: 1
labels:
  - name: "type: bug"
    color: "d73a4a"
    description: "Something is not working"
```

Quote colors, especially numeric-only colors such as `"000000"`, so YAML does not parse them as numbers.

Rules:

- `name` is required and must be non-empty.
- Label names must be unique ignoring case.
- `color` is required and must contain exactly six hexadecimal characters without `#`.
- `description` is optional and must be at most 100 characters.
- An omitted or null description is normalized to an empty description.
- Invalid configuration fails before any repository is modified.

The initial configuration intentionally contains an empty label list. Merging the controller therefore does not change existing labels. Add the actual shared label taxonomy in a separate change after the GitHub App is configured and validate it with a dry run first.

## Reconciliation behavior

For every active repository in the GitHub App installation:

- Missing canonical label: create it.
- Existing canonical label with different name casing, color, or description: update it.
- Exact match: no write request.
- Existing label absent from the canonical file: keep it unchanged.

V1 never deletes labels and never guesses semantic renames. Changing `status: waiting` to `status: blocked`, for example, creates the latter and leaves the former untouched.

The operation is idempotent: once repositories match the canonical definition, repeated runs perform no label writes.

## Triggers

The workflow runs in four modes:

- Pull requests touching the controller: unit tests only; no GitHub App token is created and no labels are modified.
- Pushes to `master` touching the controller: tests, then reconciliation with writes enabled.
- Manual `workflow_dispatch`: tests, then reconciliation. `dry_run` defaults to `true`.
- Daily scheduled reconciliation at 03:17 Asia/Tokyo: tests, then reconciliation with writes enabled.

Use the manual dry run before introducing or changing a shared label taxonomy.

## Failure handling

Canonical configuration or authentication/discovery failures stop the run before repository reconciliation can proceed.

A failure in one target repository does not stop later repositories. The controller records the failure, continues with the remaining repositories, and exits with failure after reconciliation so partial problems are visible without preventing healthy repositories from converging.

Logs contain per-repository counts for create, update, no-op, and kept labels. Tokens and private keys are never intentionally logged.

## Local tests

```bash
python -m pip install -r requirements-label-sync.txt
python -m unittest discover -s tests -v
```
