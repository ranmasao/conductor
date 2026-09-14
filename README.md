# Conductor

[![CI](https://github.com/ranmasao/conductor/actions/workflows/ci.yaml/badge.svg?branch=feature%2Fv0.5.0-state-control-separation)](https://github.com/ranmasao/conductor/actions/workflows/ci.yaml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/ranmasao/conductor/badges/coverage.json)](https://github.com/ranmasao/conductor/actions/workflows/ci.yaml)

Conductor runs coding work from explicit tickets. The coding agent writes the
implementation; Conductor manages the workflow around it.

It selects work, prepares an isolated worktree, launches a worker, preserves
the result, sends completed work to review, and integrates only accepted
changes. Product code and workflow history stay separate, and Git remains the
source of truth for both.

## Why Conductor

Coding agents are good at making changes, but a useful development workflow
also needs repository synchronization, work selection, workspace preparation,
checkpointing, publication, outcome handling, review handoff, integration, and
recovery after interruptions.

Conductor owns those surrounding mechanics outside the worker. The worker does
not publish branches, move tickets, write workflow reports, or integrate code
into the product branch. When the result or ownership of an operation is
unclear, Conductor stops instead of silently guessing.

## How It Works

```text
ticket
  -> Conductor selects it
  -> worker edits an isolated worktree
  -> Conductor preserves and publishes the result
  -> reviewer accepts or rejects it
  -> Conductor integrates accepted work
  -> done
```

The project checkout holds product code. A separate control history holds
tickets and execution reports. Local runtime state records active bookkeeping;
it is not a replacement for Git history.

## Key Properties

- Local operation in the target Git repository.
- Explicit, ticket-driven work instead of an untracked task queue.
- Isolated worker workspaces that keep active changes away from the operator
  checkout.
- Git history remains the source of truth for product and workflow changes.
- Workers write code; Conductor owns publication and workflow state.
- Review is a separate step from product integration.
- Product history and workflow history remain separate.
- Ambiguous failures stop for inspection or explicit retry.

## Current 0.5 Limitations

- Conductor 0.5 is unreleased.

The current implementation has these practical limits:

- Workflow execution is serial; general parallel worker execution is not
  implemented yet.
- Active workflow execution is hosted by a foreground process.
- Conductor does not provide system-service or background-process integration.
- There is no warm worker pool; worker sessions are ephemeral.
- Full YAML compatibility is not provided.

## Quick Start

Install this unreleased checkout, then configure it in the target project:

```sh
python -m pip install -e /path/to/conductor
cd /path/to/project
conductor init
# configure .env and project context
conductor control init
conductor check
conductor run
```

Useful read-only and recovery commands:

```sh
conductor status
conductor plan
conductor retry
```

`init` creates missing project-owned setup files without starting execution.
`control init` prepares the separate workflow history. `check` validates the
project before work starts. `run` hosts the service in the foreground; use
`run --once` for one synchronization and execution pass.

## Workflow

Tickets move from `backlog` to `todo`, then to `review`, `accepted`, and
`done`. Conductor runs only work whose dependencies are complete. Completed
worker results go to review; a reviewer decides whether accepted work can be
integrated into product history.

## Development

```sh
./dev setup
./dev check
./dev coverage
```

Coverage is diagnostic; there is no percentage gate.
