# Conductor

Conductor is a minimal bootstrap orchestrator for a software-development workflow. Product code remains on the configured product branch and canonical workflow files live only on `CONTROL_BRANCH` (default `conductor/control`) in a Conductor-owned worktree outside the product checkout.

Conductor maintains three physically separate Git surfaces: the operator checkout, the canonical control worktree, and a per-ticket execution worktree. Workers edit implementation files and provide a semantic claim; Conductor checkpoints, publishes, reports, and mutates workflow state.

## Usage

Install this unreleased checkout with `python -m pip install -e /path/to/conductor`
in the environment used for the target project. Then run `conductor` from the
root of that project. `conductor init` seeds a missing `$PWD/.env` from the
installed bootstrap template; configure at least `OPENCODE_MODEL` and the
managed workflow paths if they differ from the defaults. An existing `.env` is
never rewritten. The project must also have its normal Git remote and
authentication configured.

```sh
conductor init [--conflicts abort|backup|replace]
conductor render
conductor render --check
conductor control init
conductor run
conductor run --once
conductor check
conductor status
conductor status --json
conductor plan
conductor plan --json
```

`conductor control init` observes the configured remote and attaches an existing
control branch, or creates and publishes a fresh independent control branch when
the remote positively has no such branch. Fresh control bootstrap creates the
configured workflow directories with empty non-ticket sentinels. It does not
modify, commit, or push product files, and it does not import product-side
workflow directories.

`conductor init` creates project-local `.conductor/templates`, seeds missing
Architect and Reviewer templates plus `artifacts.toml`, and renders their skills
to the declared project targets. `conductor render` regenerates those derived
skills from the existing project-owned templates and effective safe configuration.
`conductor render --check` verifies freshness without writing. The `.env` file
remains runtime configuration and agents must not read it. Templates stay under
`.conductor`; rendered files are ordinary project artifacts and should not be
edited directly. These commands do not attach the control worktree or mutate
workflow state, and they perform no Git admission.

`conductor init` also creates an incomplete `.conductor/project.md` skeleton when
absent; it never guesses project documentation paths. Populate its NanoYAML `common`,
`architect`, and `reviewer` routes before `check`. Existing project-owned files are
preserved. The distribution-only `preinst_readme.md` documents setup and ownership;
it is never copied or rendered into a target project.

Rendered skills are materialized at the targets declared by
`.conductor/templates/artifacts.toml`; `.conductor/generated` is obsolete and is
not created, used, or automatically deleted.

Project context is routed by reference, so editing a referenced document does not
require `conductor render`. Current project documents remain the project's current
truth; Git history is historical, and Conductor does not maintain a semantic copy.

The default `run` mode is a foreground polling loop. Use `run --once` for one synchronization/execution pass. `check` validates setup without running workflow. `status` is read-only and reports what Conductor observes. `plan` is read-only and reports what Conductor would decide from one optimistic consistent snapshot; its output includes the branch, local HEAD, known remote ref, and known remote HEAD used for the decision. Neither command fetches or writes durable state. Retry if project state changes continuously while a snapshot is being collected. `--env FILE` selects a configuration file instead of `$PWD/.env`, and `--version` prints the installed version.

Use `check` for a side-effect-free configuration, checkout, control topology,
and workflow preflight. A missing but otherwise valid `STATE_DIR` is allowed;
normal execution may create it later.

`REMOTE_BRANCH` defaults to the currently checked-out branch when HEAD is attached. If set explicitly, the current branch must match it; detached HEAD is always blocked for planning and execution. See `.env.example` for the available runtime settings.

## Development Setup

For contributors working on the Conductor repository, run:

```sh
./dev setup
```

This creates the local `.venv`, installs Conductor in editable mode, and installs the pytest and Ruff development tools.

## Development Commands

All commands use the local `.venv`:

```text
./dev setup             Create the environment and install dependencies
./dev test              Run pytest
./dev lint              Run Ruff check
./dev check             Run tests and lint
./dev run [args...]     Run the checkout-local installed Conductor CLI
./dev clean             Remove named caches and build artifacts
./dev purge             Also remove .venv and named development artifacts
```

`clean` and `purge` use an explicit allowlist. They do not use `git clean` and preserve source files, configuration, `.env`, and user files.

`./dev check` is the authoritative development validation entry point. GitHub Actions runs the same `./dev setup` and `./dev check` path on pushes and pull requests using Python 3.12.

## Bootstrap workflow

```text
external Architect/Reviewer
    -> pushes new or hardening tickets into todo
    -> Conductor notices a new repository revision or todo generation
    -> fast-forward pull/sync
    -> Conductor selects one runnable todo ticket
    -> Conductor runs one worker in an isolated execution worktree
    -> Conductor checkpoints and publishes the execution branch
    -> Conductor persists the report and submits completed work to review
    -> external Architect/Reviewer inspects the result
    -> reviewer moves accepted work to accepted
    -> Conductor fast-forwards the published product branch and submits it to done
```

Workers report semantic outcomes; Conductor interprets them and owns ticket
placement. Completed work may submit the same ticket to `review`; incomplete,
blocked, or failed work preserves the same ticket in `todo`.

## Current safety rules

- The product checkout must be clean before Conductor synchronizes it. The control worktree must also be clean before it is synchronized or used for scheduling.
- Managed tickets use the explicit `BACKLOG_PATH`, `TODO_PATH`, `REVIEW_PATH`, and `DONE_PATH` directories. Missing configured directories block planning and execution; only canonical `<ID>.md` entries are tickets, while other human/editor artifacts are ignored.
- `CONTROL_BRANCH` defaults to `conductor/control`. The local control worktree is stored under `$STATE_DIR/worktrees/<repository-key>/control`; `status`, `plan`, `check`, and `run` never create it automatically.
- Each selected ticket gets the deterministic local branch `conductor/work/<ticket-id>` and worktree `$STATE_DIR/worktrees/<repository-key>/work/<ticket-id>`. The branch is durable implementation history; the worktree is a disposable active workspace. Creation, resume, and safe recreation are Conductor-owned and never use the operator checkout or control worktree.
- Execution branches start at the exact planned product code HEAD and retain the bound control revision in durable state. Control history is never merged or copied into an execution branch. Missing worktrees may be recreated from the existing branch; dirty or conflicting worktrees fail closed without reset, clean, force removal, or branch stealing.
- An execution lineage keeps its original base revision when the product branch advances independently. A valid prepared generation is not repeatedly materialized just because worker dispatch remains gated.
- The execution base identifies the ticket lineage, while the persisted control revision identifies the current scheduling attempt. A new generation may refresh control authority without creating a new branch; an interrupted attempt must retain and revalidate its original authority.
- Ticket frontmatter uses the vendored, restricted NanoYAML N0 implementation; Conductor does not depend on a general YAML library or support free-form tickets.
- Ticket identity is the filename stem. Conductor strictly validates NanoYAML N0 frontmatter, ticket metadata, globally unique IDs, dependency references, and the dependency DAG before launching a worker.
- Tickets move through `backlog -> todo -> review -> accepted -> done`. `review` awaits reviewer judgement; `accepted` awaits Conductor-owned integration; `done` means the accepted checkpoint is present in published product history. Only `todo` tickets whose dependencies are in `done` are runnable. `review` and `accepted` do not satisfy dependencies. Conductor is serial across review and integration and selects exactly one ticket for a potential worker dispatch.
- Conductor owns ticket discovery, parsing, graph validation, runnable determination, deterministic selection, selected-ticket execution binding, checkpoint commits, branch pushes, reports, and ticket movement. Ticket population is data, not initialization state; an empty valid workflow is supported.
- Conductor owns worker prompt construction. The worker receives one exact implementation assignment, a small worker-only contract, and only relevant implementation context. Canonical workflow paths, ticket paths, kanban, and Git/execution topology are Conductor details, not worker API.
- Fresh, resume, rework, and recovery prompts share one contract and differ only through a narrow work directive and relevant optional context. Ticket content is opaque assigned data; it cannot authorize canonical workflow mutation.
- Worker output is free-form unless it is exactly one strictly validated `conductor_report` tool event. `WorkerClaim` is untrusted semantic egress with `completed`, `incomplete`, or `blocked` outcomes; missing, malformed, or duplicate reports are protocol failures and do not mutate workflow.
- Conductor supplies an ephemeral reserved OpenCode tool configuration for each worker process. The worker runs in the validated execution workspace, while Conductor keeps process status separate from the worker claim and owns the resulting checkpoint commit and branch push.
- `ExecutionResult` is the canonical Conductor-owned interpretation of one execution. `ExecutionReport` is its durable structured record under `executions/<ticket-id>/<execution-id>.json` in the control worktree. Tickets remain specifications, not execution logs; `questions` and `remaining` remain structured execution data.
- Conductor derives an immutable `ExecutionPlan` from one internally consistent observed snapshot. The plan carries repository observation identity and the exact selected ticket; runtime consumes that exact ticket decision rather than performing an independent selection.
- Execution plans and status snapshots expose separate nested `observation.code` and `observation.control` Git identities. A work generation combines code and control revision identity with a deterministic fingerprint of canonical ticket files under `TODO_PATH`.
- Conductor persists the handled generation, so unchanged todo is not redispatched on every poll or after restart.
- Dirty and divergent Git states are diagnosed with paths and topology, but Conductor never automatically destroys local changes or reconciles divergent history.
- Git synchronization and workflow validity are separate boundaries: `merge_pending` covers only an unproven fast-forward transaction and is cleared once the intended HEAD is verified. A later workflow blocker is derived from current control contents and does not reopen that Git transaction.
- Completed execution submits the same ticket from todo to review. Incomplete, blocked, and failed executions preserve the same ticket in todo while retaining their execution branch and report. Reviewer acceptance moves the same ticket from review to accepted; Conductor integrates accepted checkpoints by fast-forward ancestry only and then moves them to done. No automatic rebase, merge conflict resolution, or recovery reconciliation is performed.
- Conductor stores per-repository iteration state atomically under `$XDG_STATE_HOME/conductor`, or `~/.local/state/conductor` when XDG_STATE_HOME is unset. Set `STATE_DIR` to override it. Lock files are stored under its `locks` subdirectory.
- Workers never commit, push, merge, rebase, switch branches, move tickets, write reports, or integrate into the product branch. Reviewers do not integrate product code; product-branch integration is Conductor-owned.
- A kernel-managed `flock` prevents concurrent Conductor instances for the same checkout.
- Agent sessions are intentionally ephemeral for now.
- Workers receive no control-worktree paths, control branch topology, ticket source paths, execution IDs, or branch identity. Each later attempt keeps the same ticket and execution branch while receiving a new execution ID and report.
