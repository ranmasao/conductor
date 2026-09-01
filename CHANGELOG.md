# Changelog

This file records notable changes to Conductor by released version. Entries are
ordered chronologically, from the first working release to the current release.
They describe the state shipped at each version; intermediate implementation
steps that were superseded before a release are not treated as separate product
behavior.

## 0.1.0 — 2026-08-21

First working bootstrap release.

### Added

- Added a foreground polling orchestrator for an already configured Git checkout.
- Added remote-revision observation and fast-forward synchronization before work
  dispatch.
- Added automatic OpenCode execution when actionable work exists in the configured
  todo directory.
- Added a single-pass `--once` mode alongside the default polling loop.
- Added project-local `.env` runtime configuration and an example configuration.
- Added basic locking to prevent concurrent Conductor instances for the same
  checkout.

### Changed

- Made polling the default operating mode instead of requiring a separate watch
  option.
- Kept workflow transitions, implementation commits, and Git publication owned by
  the implementation agent in this initial architecture.

### Fixed

- Hardened the bootstrap executor flow so synchronization and agent launch happen
  only under the intended remote-update and todo-work conditions.
- Clarified project-local environment-file ownership and startup behavior.

## 0.2.0 — 2026-08-22

Python port of the original shell runtime.

### Added

- Added an installable Python package under `src/conductor` with package version
  metadata and a `conductor` console entry point.
- Added `python -m conductor` execution support.
- Added a repository-local `dev` helper for environment setup, tests, linting,
  combined checks, local execution, and cleanup.
- Added pytest parity coverage for the original bootstrap behavior and helper
  tooling.
- Added Ruff configuration and explicit development dependencies.

### Changed

- Replaced the shell implementation with the Python runtime while preserving the
  existing polling, synchronization, locking, and OpenCode delegation behavior.
- Reduced the old shell entry point to a compatibility wrapper around the Python
  CLI.
- Switched development to a repository-local virtual environment and editable
  package installation.

### Fixed

- Hardened development/helper command launchers and their error handling.
- Added parity regressions around Git synchronization, agent failures, explicit
  environment files, and single-pass execution.

## 0.2.1 — 2026-08-22

First persistent execution-state and recovery release.

### Added

- Added atomic per-repository persistent state for synchronization and agent
  execution intent.
- Added persisted merge-to-agent handoff so a restart could continue an interrupted
  iteration instead of losing its scheduling intent.
- Added a bounded dirty-work recovery attempt for failed agent execution.
- Added configurable recovery prompts while keeping each OpenCode invocation a
  fresh process.
- Added prompt-variable substitution for configured workflow and repository
  coordinates.
- Added state-directory configuration and writable-location handling.

### Changed

- Moved locks and iteration state into durable state storage rather than treating
  each process invocation as stateless.
- Distinguished normal execution from recovery execution in the persisted
  lifecycle.

### Fixed

- Prevented a completed Git synchronization followed by a process interruption
  from being mistaken for an ordinary no-change poll.
- Made persistent-state writes atomic to avoid partially written state files.
- Improved visibility of recovery and startup failures.

## 0.2.2 — 2026-08-22

Recovery, synchronization, and preflight hardening.

### Added

- Added side-effect-free preflight checks for configuration, Git topology, working
  tree state, remote availability, and required runtime tools.
- Added user-level default state storage with explicit override support.
- Added deterministic handling for interruption during a recovery attempt.

### Changed

- Bound pending synchronization to exact persisted local and remote revisions.
- Replaced merge-output/message heuristics with ancestry-based Git reasoning.
- Limited recovery to states whose expected revisions and transition intent were
  persisted and could be revalidated.

### Fixed

- Prevented stale pending revisions from being silently reused after repository
  history changed.
- Hardened restart behavior around fast-forward completion and pending agent
  dispatch.
- Failed closed when Git history was divergent, ambiguous, or inconsistent with
  persisted synchronization state.
- Hardened state-directory access and startup validation before Git or OpenCode
  side effects.

## 0.2.3 — 2026-08-22

Observability and work-generation hardening.

### Added

- Added deterministic work-generation identity based on both the observed remote
  revision and current todo contents.
- Added richer dirty-working-tree and divergent-history diagnostics.
- Added persisted generation handling so unchanged todo work is not repeatedly
  dispatched after polling or restart.

### Changed

- Allowed a valid local-ahead pending execution to survive restart when its
  ancestry remained provable.
- Made remote changes and todo-content changes independently capable of producing a
  new work generation.

### Fixed

- Prevented unchanged blocked todo contents from triggering repeated agent runs.
- Hardened pending-revision reconciliation when the local checkout was ahead,
  behind, or divergent.
- Restored the exact terminal `termios` state after worker execution instead of
  leaving TTY settings modified.
- Improved Git-state diagnostics without introducing destructive automatic repair.

## 0.2.4 — 2026-08-24

Structured tickets, deterministic dependency scheduling, and worker-output safety.

### Added

- Added a vendored restricted NanoYAML N0 parser/renderer for managed workflow
  metadata.
- Added strict ticket parsing with canonical filename identity, known metadata
  fields, and explicit workflow directories for backlog, todo, review, and done.
- Added global ticket-ID uniqueness checks, dependency-reference validation, cycle
  detection, and deterministic dependency-aware runnable selection.
- Added deterministic single-ticket scheduling: only todo work whose dependencies
  are done can be selected, and one selected ticket is bound to an execution.
- Added persisted selected-ticket identity and body binding for restart/recovery.

### Changed

- Switched OpenCode execution to headless structured JSON event output.
- Treated worker stdout, stderr, tool output, and errors as inert data before
  rendering them to the operator terminal.
- Restricted the worker input to the selected assignment and required execution
  context instead of exposing the whole todo queue as executable instructions.
- Extended recovery validation to a selected ticket that remained in todo or had
  already reached review.

### Fixed

- Prevented terminal-control sequences emitted by worker output from reaching the
  operator terminal.
- Restored useful OpenCode tool-output visibility without weakening terminal-output
  isolation.
- Blocked agent launch when ticket syntax, dependency references, or the dependency
  graph were invalid.
- Hardened merge resume, blocked-dependency handling, selected-ticket persistence,
  and ticket-body binding across restart.

## 0.3.0 — 2026-08-25

Immutable planning, read-only observability, and stricter product boundaries.

### Added

- Added a command-based read-only `status` interface with workflow, Git, runnable,
  and blocked-work diagnostics.
- Added read-only `plan` output describing the exact scheduling decision without
  executing it.
- Added immutable `ExecutionPlan` objects carrying the observed repository identity
  and exact selected-ticket authority into runtime execution.
- Added GitHub Actions CI using the same repository-local setup and check path as
  development.

### Changed

- Made status, planning, and execution derive from consistent repository/workflow
  observations rather than independently selecting work at different stages.
- Included managed-directory state in workflow fingerprints so directory
  creation/removal/kind races invalidate optimistic snapshots.
- Ignored non-ticket editor or sentinel artifacts in managed workflow directories
  instead of treating them as workflow tickets.
- Kept the polling runtime alive when workflow contents were blocked, while still
  refusing unsafe execution.
- Bounded worker JSON events before decoding/parsing so oversized events are
  drained and rejected without unbounded buffering.
- Made canonical CLI subcommands the only supported command interface.

### Fixed

- Fixed reconciliation of a persisted pending execution when the local product HEAD
  changed in a way that could be classified by ancestry.
- Hardened durable pending-execution state and exact selected-ticket execution
  binding.
- Hardened snapshot freshness checks against concurrent workflow and Git changes.
- Hardened runtime branch validation and recovery admission.
- Made unknown persisted lifecycle phases fail closed.
- Strengthened filesystem scheduler integration coverage and race-boundary tests.

### Removed

- Removed the legacy shell implementation/wrapper.
- Removed pre-0.3 implicit bare-run and top-level compatibility command forms.
- Removed unbound pending-execution compatibility and scheduler-rebuild behavior.
- Removed stale migration/launcher scaffolding that no longer represented the
  supported product interface.

## 0.4.0 — 2026-09-01

Control-plane isolation and Conductor-owned execution lifecycle.

### Added

- Added an independent canonical control plane on a dedicated control branch and a
  Conductor-owned control worktree outside the product checkout.
- Added explicit `conductor control init` to attach an existing control branch or
  create a fresh independent control branch when its absence can be proven.
- Added separate code/control observations to read-only status and planning.
- Added per-ticket execution worktrees outside the product checkout and durable
  `conductor/work/<ticket-id>` implementation branches.
- Added execution-lineage binding across product revision, control revision,
  execution branch, worktree path, execution ID, and expected remote execution
  head.
- Added recursive submodule/gitlink materialization and verification for isolated
  execution workspaces, including nested submodules.
- Added a Conductor-owned worker prompt contract with narrow fresh/resume work
  directives and opaque fenced assignment content.
- Added strict typed worker egress through exactly one validated
  `conductor_report` event, keeping worker transport status separate from the
  semantic worker claim.
- Added Conductor-owned `ExecutionResult` interpretation and immutable durable
  `ExecutionReport` evidence stored on the control plane.
- Added the `accepted` workflow state between review and done.
- Added serialized Conductor-owned integration of accepted checkpoints into the
  product branch using ancestry-only fast-forward semantics.
- Added durable failed-execution metadata and explicit `conductor retry`, including
  interactive retry selection and stale-attempt validation.
- Added project bootstrap commands: `conductor init`, `conductor render`, and
  `conductor render --check`.
- Added packaged generic Architect and Reviewer protocol templates plus a
  project-owned artifact manifest and rendered role artifacts.
- Added `.conductor/project.md` as a strict project-context routing adapter for
  existing project documentation, with common and role-specific routes.
- Added a distribution-owned pre-install guide describing bootstrap ownership and
  adoption boundaries.
- Added bootstrap conflict policies for existing project files and a fresh-project
  adoption/readiness regression path.

### Changed

- Moved canonical workflow state completely off the product branch; configured
  workflow directories are now control-plane state, and product-side copies are
  rejected.
- Moved Git lifecycle ownership from the worker to Conductor. Workers now own only
  implementation edits and their semantic claim; Conductor owns checkpointing,
  branch publication, reports, ticket movement, and product integration.
- Separated the operator checkout, canonical control worktree, and per-ticket
  execution worktree into three physically distinct Git surfaces.
- Made review a mandatory serial boundary: review and accepted work block new
  implementation dispatch until resolved.
- Made dependencies satisfied only by `done`; review and accepted states do not
  unlock dependent work.
- Preserved implementation checkpoints as durable lineage instead of rebasing them
  automatically when the product branch advances.
- Made project bootstrap adapt to existing documentation and agent-instruction
  layouts rather than imposing a Conductor-specific documentation structure.
- Made generated role templates project-owned after bootstrap; runtime upgrades do
  not silently overwrite local template customizations.
- Made project-side bootstrap adoption explicitly owned by the project's existing
  change-management workflow. Conductor does not commit, push, create reviews,
  choose integration policy, or edit `.gitignore` for bootstrap changes.
- Made project-context routing reference existing documents rather than embedding
  copies, so documentation edits do not require rerendering role artifacts.
- Updated package metadata and README wording to describe Conductor as a local
  deterministic orchestrator rather than a bootstrap skeleton.

### Fixed

- Hardened control-worktree topology validation, including wrong-branch,
  unregistered, dirty, ahead, and divergent states.
- Prevented product synchronization or execution when the control plane cannot be
  validated first.
- Prevented workers from changing product checkout contents, product HEAD, branch,
  Git history, workflow state, execution reports, or publication topology without
  detection.
- Rejected worker-created commits in execution workspaces instead of allowing
  worker-owned Git history into the lifecycle.
- Added execution-branch remote-head checks to detect publication races before
  pushing.
- Hardened OpenCode transport diagnostics and supplied an ephemeral reserved
  workspace-scoped permission configuration for worker processes.
- Failed closed when product status or other required Git observations cannot be
  proven after worker execution.
- Hardened execution workspace creation/resume/recreation against branch stealing,
  unsafe cleanup, stale lineage, submodule mismatches, and unexpected paths.
- Hardened execution reports against malformed identities, duplicate/overwritten
  evidence, and inconsistent lifecycle data.
- Hardened accepted integration so already-integrated checkpoints can be completed
  idempotently while divergent product history is refused rather than rebased or
  merged automatically.
- Hardened explicit retry so it cannot bypass dirty-tree, review/accepted,
  dependency, bound-execution, product-HEAD, control-HEAD, or todo-generation
  admission barriers.
- Bound retryability to the current product revision, remote revision, control
  revision, todo generation, and immutable failed-attempt evidence.
- Hardened bootstrap against invalid repository roots, symlink escapes, foreign
  agent instructions, stale generated artifacts, and accidental rewriting of
  project-owned templates.
- Corrected fresh bootstrap semantics so `init` may produce project-side changes,
  those changes are adopted through the project's own workflow, and runtime
  readiness is checked only after returning to a clean valid checkout.

### Safety and recovery

- Preserved deterministic restart handling for `merge_pending` synchronization
  transactions when persisted revisions and Git ancestry prove the outcome.
- Preserved deterministic restart from a fully bound pre-worker `agent_pending`
  state.
- Removed the old automatic dirty-work/recovery state machine inherited from the
  earlier single-checkout architecture.
- Changed interrupted `agent_running` executions to fail closed without launching a
  second worker or inventing a recovery result. General execution recovery and
  reconciliation remain outside the 0.4.0 scope.
- Kept failed completed attempts from entering an automatic retry loop; retry is an
  explicit operator action and creates a new execution attempt while preserving
  immutable evidence from previous attempts.

### Removed

- Removed obsolete automatic recovery phases and the unreachable recovery worker
  directive.
- Removed obsolete generated-artifact staging paths and direct dependence on a
  `.conductor/generated` tree.
- Removed dead state fields, helpers, and prompt plumbing left over from the older
  agent-owned/single-checkout workflow where they no longer had a supported role.
