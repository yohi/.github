# Documentation Architecture Standard for `yohi/*`

[日本語](documentation-architecture.ja.md)

This document defines the documentation architecture, ownership model, naming conventions, localization policy, and quality gates for repositories under `yohi/*`.

The governing principle is simple:

> Keep one canonical source for each kind of information, give each reader the right entry point, and avoid maintaining the same truth in multiple places.

## 1. Goals

This standard is designed to:

- separate human-facing documentation from agent-facing instructions;
- keep README files focused on discovery and onboarding;
- prevent README files from becoming specifications, runbooks, or agent playbooks;
- use English as the canonical language;
- provide Japanese translations only for human-facing documentation where useful;
- keep normative and machine-consumed documents single-source;
- distinguish repository-level canonical documents from topic-specific documentation through naming conventions;
- make documentation easy to navigate for users, contributors, operators, and AI agents.

## 2. Core architecture

A mature repository should generally follow this shape when the corresponding documents are needed:

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

Not every repository needs every file. Create only the documents whose responsibilities actually exist in the project.

## 3. Responsibility model

Each document class has one primary responsibility.

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

The most important rule is:

> Do not create multiple canonical sources for the same information.

## 4. README.md

### Role

`README.md` is the project entry point. It should primarily act as:

1. a project landing page;
2. a quick-start guide;
3. a documentation router.

A README is not the complete technical specification of the project.

### Canonical README content

A README should contain, as applicable:

- project name;
- one-line value proposition;
- what the project is and why it exists;
- status or important notices;
- badges;
- quick start;
- key features;
- representative usage;
- a high-level architecture overview;
- only the most important configuration;
- links to detailed documentation;
- basic development instructions.

### Do not use README as

Do not make `README.md` the canonical source for:

- complete architecture specifications;
- HTTP contracts;
- MCP tool references;
- complete configuration references;
- environment-variable catalogs;
- deployment runbooks;
- operations runbooks;
- migration manuals;
- exhaustive troubleshooting catalogs;
- AI agent playbooks.

Move those responsibilities to dedicated documents and summarize them in the README with links.

## 5. Canonical README structure

The default structure is:

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

Sections that do not apply should be omitted rather than kept empty.

## 6. Reader journey

README order should follow the reader's questions, not the implementation's internal structure.

```text
What is this?
      ↓
Why should I care?
      ↓
Can I use it?
      ↓
How do I try it?
      ↓
How do I use it?
      ↓
How does it work?
      ↓
Where are the details?
```

As a result, avoid placing the following near the top of a README unless they are essential to understanding the product itself:

- repository layout;
- internal modules;
- storage internals;
- complete environment-variable lists;
- migration details;
- release procedures;
- agent tool-selection rules.

## 7. Quick Start

The Quick Start should take a new reader to the first successful outcome with the minimum necessary steps.

It should normally contain only:

1. minimum requirements;
2. installation;
3. minimal configuration;
4. one execution path;
5. an expected result or success condition.

Do not turn Quick Start into the complete installation, deployment, migration, or troubleshooting manual.

Prefer one obvious Quick Start. Specialized workflows such as development sandboxes belong under `Development` or a dedicated guide.

## 8. Reader routing

When a repository serves clearly different audiences, use explicit routing.

For example:

```markdown
## Get Started

| I want to... | Start here |
| --- | --- |
| Use the service | [Quick Start](#quick-start) |
| Develop locally | [Development](#development) |
| Deploy my own instance | [Deployment](docs/deployment.md) |
| Configure an AI agent | [Agent Instructions](AGENTS.md) |
```

Typical reader roles include:

- user;
- developer;
- operator;
- AI agent.

Routing should remain short. The full procedure belongs in the target document.

## 9. Badges

Badges are status indicators, not decoration.

Use approximately two to five badges that communicate meaningful project state.

Preferred order:

```text
CI
→ CodeRabbit
→ Release
→ Runtime / Protocol / Ecosystem
→ License
```

Recommended badge categories include:

- CI / tests;
- CodeRabbit PR reviews;
- release / version;
- runtime / language;
- protocol;
- package registry;
- license.

Avoid walls of vanity badges such as stars, forks, repository size, code size, issue count, PR count, or other low-value statistics.

## 10. SPEC.md

### Role

`SPEC.md` is the normative technical source of truth for implementation correctness.

It may be read by both humans and AI agents, but precision takes priority over tutorial-style readability.

### Typical contents

- detailed architecture;
- design invariants;
- state transitions;
- failure semantics;
- protocol behavior;
- HTTP contracts;
- request and response rules;
- data-consistency rules;
- security guarantees;
- compatibility guarantees;
- acceptance criteria.

### Localization

`SPEC.md` is English only.

```text
SPEC.md
SPEC.ja.md   <- do not create
```

If Japanese architectural explanation is useful, create a human-oriented document such as `docs/architecture.ja.md` instead of translating the normative specification.

## 11. AGENTS.md

### Role

`AGENTS.md` is the canonical source for repository-specific AI agent instructions.

### Typical contents

- mandatory constraints;
- allowed and forbidden behavior;
- tool-selection rules;
- verification requirements;
- repository-specific workflows;
- test requirements;
- context-loading policy;
- generated-file rules;
- safety constraints;
- implementation conventions.

### Localization

`AGENTS.md` is English only.

```text
AGENTS.md
AGENTS.ja.md   <- do not create
```

Do not duplicate a complete agent playbook in README. The README may contain a short route such as:

```text
For automated setup, ask your coding agent to follow AGENTS.md.
```

## 12. Human-facing docs/

The `docs/` directory contains detailed documentation whose primary consumer is a human.

Typical documents include:

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

Human-oriented architecture explanation. Prefer comprehension and context over normative precision. Link back to `SPEC.md` where exact behavior matters.

### configuration.md

Complete configuration reference, including:

- settings and environment variables;
- defaults;
- required versus optional values;
- examples;
- security implications.

### deployment.md

Deployment procedure, including as needed:

- setup;
- secrets;
- CI/CD;
- production deployment;
- verification.

### operations.md

Operational runbook, including as needed:

- monitoring;
- alerting;
- recovery;
- rollback;
- incident handling;
- quota handling.

### migration.md

Version migration procedure. README should usually mention the breaking change and route readers here for the actual migration steps.

## 13. Language policy

### Canonical language

English is the canonical language for documentation across `yohi/*`.

Examples:

```text
README.md
docs/architecture.md
docs/configuration.md
```

### Japanese localization

Only human-facing documentation should be localized into Japanese when useful.

Use the suffix:

```text
<name>.md
<name>.ja.md
```

Examples:

```text
README.md
README.ja.md

docs/architecture.md
docs/architecture.ja.md
```

Do not use `README.en.md` as the canonical README. GitHub should render `README.md` as the default English entry point.

## 14. Translation scope

### Normally localized

Japanese versions should normally be considered for:

- README;
- Getting Started;
- installation or setup guides;
- primary usage documentation.

### Localize when useful

Localize when the value exceeds the maintenance cost:

- architecture;
- configuration;
- deployment;
- operations;
- migration;
- contributing;
- troubleshooting.

### Do not localize

Do not create Japanese duplicates for:

- `AGENTS.md`;
- `SPEC.md`;
- schemas;
- skills;
- prompts;
- machine-consumed configuration;
- generated documentation;
- normative protocol definitions.

## 15. Translation source of truth

English and Japanese are not two independent canonical documents.

The relationship is always:

```text
English canonical
       ↓
Japanese translation
```

Correct update flow:

```text
README.md
   ↓ update
README.ja.md
   ↓ synchronize translation
```

If a factual problem is discovered in the Japanese version, fix the English canonical document first and then resynchronize the translation.

Japanese translations may include a notice such as:

```markdown
> [!NOTE]
> This document is a Japanese translation of the [English version](README.md).
> If the contents differ, the English version is authoritative.
```

## 16. Language switch

Place a link to the alternate language near the top of a localized human-facing document.

English README:

```markdown
[日本語](README.ja.md)
```

Japanese README:

```markdown
[English](README.md)
```

A page does not need to link to itself.

## 17. File naming conventions

### Repository-level canonical documents

Documents with repository-wide, special semantics use uppercase filenames.

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

Documents under `docs/` use lowercase kebab-case.

```text
docs/architecture.md
docs/configuration.md
docs/agent-setup.md
docs/http-contract.md
docs/routing-weights-rationale.md
docs/cloudflare-ai-gateway-custom-provider.md
```

Japanese versions use `.ja.md`:

```text
docs/architecture.ja.md
docs/agent-setup.ja.md
```

General rule:

> Repository-level canonical documents use uppercase filenames. Topic-specific human documentation uses lowercase kebab-case.

## 18. CHANGELOG.md

`CHANGELOG.md` is English only by default.

Reasons include:

- release tooling often generates or updates it;
- release titles, commits, and pull requests are easier to keep aligned in one language;
- maintaining two release histories creates high synchronization cost;
- one canonical historical record is sufficient.

```text
CHANGELOG.md
CHANGELOG.ja.md   <- normally do not create
```

## 19. CONTRIBUTING.md

`CONTRIBUTING.md` is human-facing and may have a Japanese translation when useful.

```text
CONTRIBUTING.md
CONTRIBUTING.ja.md
```

Small repositories that do not actively accept external contributions may keep only the English version.

## 20. SECURITY.md

`SECURITY.md` is human-facing but contains operationally important information whose duplication can be risky.

English-only is acceptable by default.

A Japanese version may be added when Japanese-language security reporting is expected, but supported-version information and reporting contacts must remain synchronized.

## 21. Single Source of Truth matrix

| Information | Canonical source | Japanese localization |
| --- | --- | --- |
| Project overview | `README.md` | `README.ja.md` |
| Quick Start | `README.md` | `README.ja.md` |
| Main features | `README.md` | `README.ja.md` |
| High-level architecture | `README.md` | `README.ja.md` |
| Detailed architecture | `SPEC.md` | Human explanation only |
| Design invariants | `SPEC.md` | No |
| Protocol contract | `SPEC.md` or dedicated normative technical reference | No |
| MCP tool contract | Normative technical reference | No |
| Agent behavior | `AGENTS.md` | No |
| Configuration reference | `docs/configuration.md` | Optional |
| Deployment | `docs/deployment.md` | Optional |
| Operations | `docs/operations.md` | Optional |
| Migration | `docs/migration.md` | Optional |
| Contribution guide | `CONTRIBUTING.md` | Optional |
| Release history | `CHANGELOG.md` | No |
| Security policy | `SECURITY.md` | Optional |

## 22. Information flow

The intended documentation journey is:

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

For Japanese readers:

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

## 23. Duplication rules

### Agent instructions

Do not copy the same agent rules into README, `AGENTS.md`, and skills.

Choose one canonical instruction source and route to it.

### Specifications

Do not maintain the same protocol contract independently in README, `SPEC.md`, and `docs/http-contract.md`.

One document owns the contract; other documents summarize and link.

### Configuration

Do not independently maintain the same configuration table in README, `.env.example`, and `docs/configuration.md`.

A recommended responsibility split is:

```text
.env.example
    -> machine-usable input template

docs/configuration.md
    -> human explanation and complete reference

README
    -> only the most important settings and routing
```

## 24. Repository archetypes

Do not force every repository into one identical README template. Use the common principles with an archetype appropriate to the project.

### Type A: Library / Plugin

Examples: `justice`, `akane`

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

Examples: `nexus`, `chronos-graph`

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

Examples: `octg`, `opencode-cloudflare-ai-gateway-chatgpt`, `ocr-app`

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

Examples: `cf-ai-gw-dynamic-routing`, `dotfiles-ai`

A repository that is not directly installed or executed by an end user may use:

```text
## How to Use This Repository
```

instead of forcing a conventional `Quick Start` section.

## 25. README size guidance

Line count is not a quality metric, but it is a useful warning signal.

Typical guidance:

- approximately 100–300 lines: healthy for many libraries and plugins;
- 300–500 lines: review whether detailed information should move out;
- 500+ lines: strong signal to check for embedded specifications, references, runbooks, migrations, or full agent instructions.

A long README is acceptable when the information genuinely belongs at the entry point, but length should be justified by reader value.

## 26. Quality gates

### README first-screen test

The opening area should answer:

- [ ] What is this project?
- [ ] Why does it exist?
- [ ] Who is it for?
- [ ] Is there a status or breaking-change notice?
- [ ] What is the current CI/release state?

### Quick Start test

A new user should quickly be able to do at least one of the following:

- [ ] install the project;
- [ ] run it;
- [ ] call the API;
- [ ] configure the client;
- [ ] delegate setup to an AI agent;
- [ ] understand how to use the repository correctly.

### SSOT test

- [ ] Agent rules are not duplicated.
- [ ] Protocol definitions have one canonical source.
- [ ] Configuration reference has one canonical source.
- [ ] Migration procedure has one canonical source.
- [ ] Japanese documentation is derived from English.

### Structure test

- [ ] There is one H1.
- [ ] Heading hierarchy is semantically correct.
- [ ] H3 does not appear before the relevant H2.
- [ ] The document can be understood by scanning headings.
- [ ] Quick Start appears before deep implementation detail unless architecture itself is essential to understanding the product.

### Naming test

- [ ] Repository-level canonical documents use uppercase filenames.
- [ ] `docs/` files use lowercase kebab-case.
- [ ] Japanese files use `.ja.md`.

### Localization test

- [ ] Only human-facing documentation is translated.
- [ ] English is canonical.
- [ ] Japanese is derived.
- [ ] `AGENTS.md` is not translated.
- [ ] `SPEC.md` is not translated.
- [ ] Japanese-only factual changes are not maintained independently.

## 27. Canonical summary

The architecture can be summarized as:

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

Naming follows the same model:

```text
README.md
SPEC.md
AGENTS.md
CHANGELOG.md
```

for repository-level canonical documents, and:

```text
docs/architecture.md
docs/configuration.md
docs/deployment.md
```

for topic-specific human documentation.

Japanese localization uses:

```text
README.ja.md
docs/architecture.ja.md
```

## 28. Governing principles

1. **README is the entry point, not the specification.**
2. **SPEC is the source of truth for technical correctness.**
3. **AGENTS is the source of truth for AI agent behavior.**
4. **Detailed human-oriented explanation belongs under `docs/`.**
5. **Do not create multiple canonical sources for the same information.**
6. **English is the canonical language.**
7. **Japanese localization is limited to human-facing documentation.**
8. **Agent-facing and normative technical documents are not translated.**
9. **Repository-level canonical documents use uppercase names; topic-specific docs use lowercase kebab-case.**
10. **Documentation quality is measured by how quickly the intended reader reaches the correct information, not by how much information is stored in one file.**
