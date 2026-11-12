---
name: timespent
license: MIT
description: Estimate project work time from Git history and optional user activity logs. Use for questions about time spent, sessions, daily activity, or message volume. Produces a terminal summary, JSON, and a standalone local HTML report.
compatibility: Requires Python 3.10+ and Git unless --no-git is used. Uses only the Python standard library; no network access required.
metadata:
  author: averines
---

# Estimate project work time

Use available tools; no specific agent, command interface, or profile location
is required. Respond in the user's language. The script uses only the Python
standard library. Before running it, confirm which sources are available and
which project and person they describe.

## Sources and boundaries

- Default: Git history across all local refs (`git log --all`), using author dates.
  `--author` matches a literal name/email substring in Git only.
- Optional: explicitly supplied `--activity` files in the shared
  [JSONL format](references/activity-format.md). Do not discover or read agent
  logs automatically. If converting an export, include only verified user
  messages for this project and person. Convert it to the required JSONL format;
  do not pass an unsupported export directly.
- Without message data, report message count and volume as unknown. Missing
  logs do not prove that no work occurred or that records were deleted.
- With multiple Git authors, the estimate uses one combined event stream.
  It does not sum person-hours. For a personal estimate, filter the intended
  author and supply matching activity logs.
- Do not change Git trust settings or history for a report. Report Git failures
  and follow environment rules.

## Run

Find `timespent.py` relative to the loaded `SKILL.md`. Replace the script and
project paths in these examples with their actual paths:

```sh
python3 /path/to/skill/timespent.py --repo /path/to/project
```

```powershell
python 'C:/path/to/skill/timespent.py' --repo 'D:/path/to/project'
```

If `python` is unavailable on Windows, check `py -3`. The script needs Python
3.10+ and its standard library; do not install third-party packages to run it.

Options:

- `--activity PATH`: explicit JSONL input; repeat for multiple files.
- `--no-git`: use supplied activity events only, without requiring a repository
  or invoking Git.
- `--html PATH`: standalone local HTML report with charts.
- `--fragment PATH`: HTML fragment without the document wrapper.
- `--json PATH`: report data and limitations.
- `--gap`, `--cap`, `--lead`, `--tail`: model parameters in minutes.

Without `--repo`, use the current directory. Without output paths, the script
prints only to the terminal. Redirected output and errors use UTF-8.
Write reports to a temporary directory unless the user chose another location.
Do not overwrite existing files. Reports omit full message text but may contain
private paths and metadata. Do not publish inputs or reports automatically.

## Model and limits

The script estimates time from event timestamps. It does not measure attendance
or focused work.
Waiting, autonomous tool execution, concurrent activity, and automated or
imported commits can distort the estimate.

A gap greater than `--gap` (default 180 minutes) starts a new session. Count up
to `--cap` (30) minutes between consecutive events, plus `--lead` (10) before
and `--tail` (15) after each session. Count overlapping intervals once. Split
minutes across local calendar days at midnight without splitting the session.
Calendar dates and hours use the machine's local time zone.

Use the same model for every source, including Git-only runs. Do not add hidden
calibration or extrapolate into periods without logs. Event coverage is unknown.
Sensitivity uses `cap/lead/tail` multiplied by 0.5 and 2, rounding fractional
minutes down. This shows dependence on parameters, not a confidence interval
or bounds on actual work time.

## Verify and report

1. Wait for successful completion and verify that requested files exist. Do not
   present partial output from a failed run as a completed report.
2. Report estimated hours, event period, sessions, commits, and message coverage.
   Use the script's figures; do not claim access to sources you did not use.
3. Include applicable `caveats`, especially Git-only coverage, combined authors,
   and the difference between estimation and measurement.
4. Link the generated HTML. Open a browser or publish only when the user or
   applicable project rules authorize it.
