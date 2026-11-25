# Agent skills

Six skills for coding agents: inspect an environment, review committed changes,
resolve findings, run a bounded review cycle, examine ideas from distinct
perspectives, and estimate project work time.

Instructions are in English. Agents respond in the user's language. The skills
use available project tools rather than requiring a specific agent or interface.

## Skills

| Skill | Purpose | Requirements |
| --- | --- | --- |
| [check-env](skills/check-env/SKILL.md) | Report available CLI tools and Python distribution metadata; never install packages | PowerShell 5.1+ or Bash 3.2+; optional Python 3.8+ |
| [code-review](skills/code-review/SKILL.md) | Read-only defect review of an explicit Git commit or range, at high or medium depth | Git and the target project's verification tools |
| [fix-review](skills/fix-review/SKILL.md) | Independently verify findings, fix confirmed in-scope defects, and check the result | Git, an exact review target, and its report |
| [review-cycle](skills/review-cycle/SKILL.md) | Coordinate review and fixes with explicit stop conditions and round limits | Git, code-review, and fix-review |
| [perspectives](skills/perspectives/SKILL.md) | Six Thinking Hats, Dreamer / Realist / Critic, or diagnosis followed by a rework plan | Access to the material being analyzed |
| [timespent](skills/timespent/SKILL.md) | Estimate work time from Git and optional explicit activity logs; generate terminal, JSON, and local HTML reports | Python 3.10+; Git unless using `--no-git` |

## Install

Use an agent that supports [Agent Skills](https://agentskills.io/specification).
The [skills CLI](https://github.com/vercel-labs/skills) requires Node.js 22.20+.

List skills, install one, or install the review workflow together:

```text
npx skills add averines/skills --list
npx skills add averines/skills --skill check-env
npx skills add averines/skills --skill code-review fix-review review-cycle
```

Select the intended agent when prompted. Installation is project-local by
default; add `-g` for global installation. To try this checkout, use
`npx skills add . --list` or `npx skills add . --skill check-env`.

Each skill is a complete folder under [skills/](skills/). For manual installation,
copy the full folder into your agent's supported skills directory. Install all
three review skills for review-cycle. Standalone fix-review can discover project
checks without the optional shared reference from code-review.

## Usage examples

- “Check the tools and Python environment available for this project.”
- “Review commit `<hash>` at high depth without changing files.”
- “Review the small commit `<hash>` using `code-review` at `medium` depth.”
- “Verify this review report and fix its confirmed issues within the task.”
- “Run a review cycle on `<base>..<tip>`.”
- “Evaluate this design with Six Thinking Hats.”
- “Estimate time spent on this repository for author `<name>`.”

Review targets must be existing commits or explicit ranges. Working-tree and
staged changes are not targets for the review workflow. The default review cycle
allows up to three rounds, then one full second pass of up to two rounds if needed.
Reaching a limit does not establish success. Independent review requires available
and authorized delegation. The user, project rules, or the agreed plan can make
it a completion requirement.

Environment checks distinguish `OK`, `MISSING`, and `UNKNOWN`; a version or
metadata check does not prove authentication, importability, or project behavior.
The time estimate is an event-based heuristic, not measured attendance or a
confidence interval. It reads activity logs only when explicitly supplied in
the documented format. Do not publish personal logs or generated reports by default.

## License

[MIT](LICENSE). Copyright (c) 2026 averines. Each skill includes a copy of the license
so its terms remain available when the skill is installed separately.
