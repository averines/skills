---
name: check-env
license: MIT
description: Inspect available CLI tools and Python distributions before a task or when a command fails. Report versions, missing tools, and failed probes on Windows or Bash environments. Use to check prerequisites or investigate a suspected missing dependency; does not install anything.
compatibility: Windows PowerShell 5.1+ or Bash 3.2+. Python 3.8+ is optional for Python distribution checks. No network access or third-party Python dependencies required.
metadata:
  author: averines
---

# Environment check

Use the current environment's tools. No specific agent, command interface, or
profile directory is required. Report in the user's language.

## Run the inventory

Find the scripts relative to this loaded `SKILL.md`. Do not assume an install
path. Run the script in the environment that will run the task:

- Windows: `powershell -NoProfile -File /path/to/skill/check-packages.ps1`
  (`pwsh` is also supported).
- Linux, WSL, or macOS: `bash /path/to/skill/check-packages.sh`.

Check Windows and WSL separately. A tool available in one may be absent from
the other. Do not bypass an execution policy to run the script.

The default inventory includes common CLI tools and optional Python packages
for documents and data. These are not required dependencies for every project.
Use `-SkipPythonPackages` (PowerShell) or `--skip-python-packages` (Bash) for CLI only.
To inspect a project's interpreter, pass `-Python /path/to/python` or
`--python /path/to/python`; otherwise the script chooses an available Python.

The scripts require no user input. Do not install, download, refresh package
managers, send telemetry, or change the environment during this check.
Exit code zero means the inventory finished. Inspect each tool's status separately.

## Interpret the results

- `OK`: a CLI version command succeeded, or the selected Python has metadata
  for the distribution. This does not establish authentication, permissions,
  feature support, successful imports, or operation in the target project.
- `MISSING`: the executable was not found, or the selected Python has no metadata
  for the named distribution.
- `UNKNOWN`: a version or metadata check failed. Report the failed check;
  do not claim the tool or package is absent. Investigate if relevant to the task.

Report versions, the exact Python interpreter, missing task prerequisites, and
checks you could not perform. Do not present optional tools as required installs.
Then verify the specific feature or operation the task needs.

## Installation recommendations

Treat suggested commands as examples, not completed actions. Before any install,
check the project's dependency files and environment rules. Use its existing
Python environment. If none exists, use a virtual environment; do not bypass
system-Python protections. Run installs only when authorized.

The Windows script prints WinGet commands for known tool IDs. Verify the package
and version before an authorized install. The Bash script points to platform
package managers and official documentation. It does not select apt for every
Linux distribution or download remote installers.

See [tool purposes and limitations](packages.md). Recheck availability after an
authorized install in the environment used by the task.
