# Conductor Pre-Install Guide

## What Conductor Adds

An existing software project already has its own product history, documentation,
agent instructions, and rules for accepting changes. Conductor adds a small
project-local adapter and protocol artifacts on the product side, plus a separate
control plane for workflow state.

Conductor does not take ownership of the project's documentation layout or its
change-management process. The project remains responsible for deciding what its
documents mean and how changes become accepted project state.

## Ownership Domains

Project and product side:

- `.conductor/project.md`
- `.conductor/templates/`
- rendered Architect and Reviewer artifacts
- `.env`
- existing project documentation and agent instructions

These files live in or beside the normal product checkout and are subject to the
project's own change-management rules.

Conductor control side:

Canonical workflow state is initialized separately through the control plane. It
lives in the configured control branch and worktree; it is not imported into the
normal product branch.

## Prerequisites

Before attaching Conductor, have:

- an existing Git repository checkout
- the intended product branch checked out
- a configured remote
- working Git authentication
- enough existing project documentation for Architect and Reviewer work
- knowledge of which existing documents should be routed to those roles

Conductor does not require a particular documentation layout. The project does
not need `README.md`, `AGENTS.md`, `CLAUDE.md`, or `docs/ARCHITECTURE.md` unless
those files are part of its own conventions.

## Project Context Adapter

`.conductor/project.md` is a routing adapter, not a documentation replacement.
Its NanoYAML frontmatter is machine-readable and its Markdown body is human
guidance. The frontmatter explicitly points to existing project documents under
`common`, `architect`, and `reviewer`.

Architect receives `common` plus `architect`. Reviewer receives `common` plus
`reviewer`. Conductor validates that these are safe, readable project-relative
files, but it does not discover, classify, or interpret their contents.

For example:

```text
---
"type": "conductor.project"
"common":
  - "README.md"
"architect":
  - "docs/architecture.md"
"reviewer":
  - "docs/testing.md"
---
```

## Bootstrap Procedure

1. Run the project-side bootstrap.

   ```sh
   conductor init
   ```

2. Inspect the generated project-side artifacts and populate `.conductor/project.md`
   with the existing documentation used by the project.

3. Review and incorporate the generated or updated project-side bootstrap artifacts
   using the project's normal change-management workflow. Conductor does not know
   whether that means a direct commit, feature branch, pull request, merge request,
   Gerrit review, Jenkins-controlled process, or something else.

4. Return to the intended product checkout in a clean, valid state.

5. Initialize or attach the Conductor control plane.

   ```sh
   conductor control init
   ```

6. Validate readiness.

   ```sh
   conductor check
   ```

`conductor init` may create `.env`, `.conductor/project.md`, templates, and
generated role artifacts, so it may make the product checkout dirty. The project
workflow decides how those changes are accepted. Runtime execution remains
fail-closed until the resulting checkout is clean and valid.

## Project Decisions

Conductor does not:

- commit product changes
- push product branches
- create pull requests or merge requests
- select a project integration policy
- edit `.gitignore`
- decide whether `.env` is tracked, ignored, or managed another way
- reorganize project documentation
- replace existing agent instructions

The project decides all of these. Conductor only creates deterministic bootstrap
artifacts and validates the resulting operational state.

## Upgrading an Existing Conductor Project

Upgrading the Conductor runtime does not automatically upgrade project-owned
Architect or Reviewer templates. A pre-0.4 project may retain older templates
without project-context routing after the runtime is upgraded.

The project owner must explicitly adopt or merge the newer generic templates into
the project-owned templates, then regenerate declared artifacts:

```sh
conductor render
```

This is separate from fresh bootstrap. Conductor does not perform automatic
template migration or semantic merging.

## Distribution And Current Truth

`preinst_readme.md` is part of the Conductor source/release distribution and is
setup guidance. It is not copied into target projects, rendered as a project
artifact, or treated as project canon. An installed Python package is not required
to expose this file at runtime.

The target project owns `.env`, `.conductor/project.md`, project templates,
generated role artifacts, and existing documentation. Current project documents
are current project truth as defined by that project; Git history contains
historical versions. Conductor does not maintain a separate semantic copy.
