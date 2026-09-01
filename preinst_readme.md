# Conductor Pre-Install Guide

Attach Conductor to an existing Git checkout on its normal product branch, with a
configured remote, working authentication, and the project's existing documentation
and agent context ready for its own work.

Conductor does not require `README.md`, `AGENTS.md`, `CLAUDE.md`, or a particular
`docs/` layout. Identify the documents that already provide project context. Do not
delete, normalize, replace, or reorganize existing agent files, skills, prompts, or
documentation.

Before bootstrap, prepare `.conductor/project.md`. Its NanoYAML frontmatter explicitly
routes `common`, `architect`, and `reviewer` paths to existing project files. Conductor
validates those paths but does not classify or interpret their contents.

The supported sequence is:

```text
conductor init
conductor control init
conductor check
```

Prepare `.env` and select its runtime settings as needed. `init` may create an
incomplete `.conductor/project.md` skeleton, but `check` will not pass until routing
contains at least one existing readable file.

Conductor distribution defaults and this guide are not project canon. The target owns
`.env`, `.conductor/project.md`, `.conductor/templates/`, `artifacts.toml`, generated
role artifacts, and its existing documentation. Upgrading Conductor does not rewrite
project-owned role templates. Current project documents remain the project's current
truth; Git history is historical, and Conductor does not maintain a semantic copy.
