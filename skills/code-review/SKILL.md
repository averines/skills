---
name: code-review
license: MIT
description: Review an explicit Git commit or range without changing source files. Use for defect-focused code review, requirement checks, and risks in affected workflows, at high or medium depth.
compatibility: Requires Git and an existing commit or range. Runtime checks depend on the target project's tools and environment.
metadata:
  author: averines
---

# Code review

Review the target supplied in the current request. Accept optional depth
`high` (default) or `medium`; `<depth> for <target>` is also valid input.
Read the actual request instead of relying on argument placeholders.

Do not edit source files, the Git index, refs, or the user's branch. Do not run
`git checkout`, `stash`, `reset`, `clean`, or `commit`. Do not invoke fix-review
or review-cycle. You may create temporary copies and verification artifacts
outside the user's source files, subject to environment rules.

Check command side effects before execution. Do not update snapshots or other
expected-output files automatically. Do not test against live user data or production.
Respond in the user's language; preserve identifiers and protocol labels.

## 1. Resolve the target

Require a Git repository and one clearly identified existing commit or range.
Outside Git, state the limitation and stop. Working-tree changes, staged changes,
and individual files are not valid targets. Do not create a repository or commit
to enable review. If the target is missing or ambiguous, ask for the hash or range.
Do not choose HEAD, all unpushed history, or working changes yourself.

Use `base` for the comparison's starting tree and `tip` for its ending commit.

- **Commit:** resolve to a full hash. Compare an ordinary commit with its
  parent, or a root commit with an empty tree. For a merge, identify the
  comparison parent; ask if the context does not establish it. A combined diff
  is not a complete replacement for that comparison.
- **Range `A..B` or `A^..B`:** resolve both endpoints and name the base and tip.
  Review the diff between those trees; list `git log base..tip` separately.
  In `A^..B`, the base is A's first parent and A is included. A root has no
  `A^`. Check ancestry; ask about intent if the base is not an ancestor of tip.
- **Root through tip, inclusive:** require an explicitly selected full history
  and a verified root ancestor of tip. Include root in the commit list and
  compare the empty tree with tip. Do not call this `root..tip`, which excludes
  root from the commit list.

Read related code and consumers from the relevant Git trees. Do not use another
checkout version as their replacement. Identify base and tip versions in the report.

Both depths require the entire target diff:

- `high`: check affected workflows and their direct system connections.
- `medium`: check direct connections and regressions from fixes.

Do not skip files because of depth. Split large targets into related parts or
commits, then check their combined effects. Do not report an intermediate defect
already fixed at tip. State any parts you did not read.

## 2. Establish requirements and environment

Read project instructions, the task, referenced documents, and included commit
messages. Compare their requirements with code, tests, manifests, configuration,
and CI in the target version. Check for missing implementation and unauthorized
scope changes; cite the relevant requirement. Follow this project's rules,
not conventions from another repository. If the task is unavailable, state
that limitation and do not invent requirements.

Identify the actual language, platform, subproject, OS, shell, runtime or SDK,
dependency manager, target versions, and commands for checks. Do not
assume npm, Docker, WSL, or a browser. Use the current shell's syntax and quote
paths correctly. A configuration file does not prove that its SDK, service,
emulator, tool, or credentials are available. Check Windows and WSL separately.

Find commands in project rules, CI, manifests, and existing scripts. Do not
assume a fixed priority among these sources. Run focused checks first, then
required project checks. Do not install tools, change dependencies, or run migrations
without authorization. Consult [verification examples](references/verification.md)
when the environment or required coverage is unclear.

## 3. Inspect the change and affected workflows

1. Read the full diff, including relevant configuration, resources, tests, and
   documentation. Do not judge risk by file size or extension. For generated
   files, identify their source and how to reproduce them. Inspect executable output too.
2. Compare behavior before and after. Follow callers, callees, contract consumers,
   data schemas, and state writes and reads as applicable. Find all consumers of
   changed shared functions or types.
3. Check logic, access boundaries, compatibility, concurrency, lifecycle,
   resources, performance, and failure handling. For a fallback, establish which
   failures it hides, what the user sees, and whether data survives. Follow
   project policy. Use history when needed to understand a removed safeguard.
4. Before a check, define the expected observable result and required conditions.
   Check the key assumption first, including external conditions. Documentation
   can establish that a feature is supported. Separately check that it is present,
   configured, and working in this environment. Use current official documentation
   for unfamiliar APIs or versions.
5. Check which failures existing tests detect. The existence of tests, mocks, or
   coverage figures does not establish correct behavior. Run relevant checks.
   Record command, cwd, code version, result, and key output. The executed copy
   must match the target: verify its hash and local changes. If the checkout
   differs or has local changes, use an authorized temporary copy of the
   required tree without changing user refs. Account for
   dependencies, submodules, LFS, and runtime resources. If this is unavailable,
   report the obstacle; tests of another version do not verify this target.
6. For UI or interactive changes, reproduce the affected workflow in its target
   runtime: a browser for web, a loaded extension for extension behavior, or the
   app, engine, or emulator for native code. Exercise relevant failure and lifecycle
   branches. Use suitable calls or tests for CLI, API, or library changes. Discover
   available tools first: browser integrations are one option, not a requirement.
   Use the project's test runner when appropriate. Do not require Playwright for
   native code. State observed obstacles without inventing causes. A build, headless run,
   or screenshot does not verify all interactive behavior.
7. Make a separate `Insight` pass over weak points in the affected workflow and
   direct dependencies: contracts, persistence, errors, and outcome verification
   as applicable. At `medium`, restrict this pass to paths affected by fixes.
   Do not turn it into a repository-wide audit.

Wait for checks to finish. Starting a process or server is not a passed check.
Separate your runs, the author's or CI results, and tests you only read.
Complete available checks. If a runtime is unavailable, name the scenarios
you could not verify.

## 4. Filter findings

A finding needs concrete conditions, a significant consequence, and a check
that could show the defect is fixed. Show that the diff introduced or worsened
it and that it remains at tip. Put pre-existing, unaffected issues in `Insight`. An intended
behavior change is a defect only if it violates requirements, contracts, or
constraints. Exclude taste, cosmetics, generic advice, and missing tests alone.

Try to disprove each candidate using code, configuration, and checks:

- `CONFIRMED`: reproduced, or unavoidable on a clearly established code path
  under conditions you have checked. Give prerequisites, steps, expected result,
  and actual result.
- `PLAUSIBLE`: evidence supports a concrete scenario, but a required condition
  or proof is missing. State the check needed to confirm it. This verdict does
  not authorize a fix.

An unavailable check does not confirm or disprove a defect. Exclude disproved
candidates. Use one finding per root cause; separate causes that need separate
fixes. Link the smallest relevant location in the target version. Put context
in evidence. For deletions, identify the old version and deleted location.

Severity describes consequences; verdict describes evidence:

- `blocker`: critical failure of a core workflow, security, or data integrity;
  blocks release.
- `high`: serious defect under explicit conditions; needs priority correction.
- `medium`: practical defect in a specific workflow.
- `low`: small concrete defect with an explained consequence.

Do not inflate severity because of uncertainty, absent tests, or consumer count.

## Report

Start with:

```text
Target: <full hash or resolved base..tip; explicit comparison base for root>
Depth: <high|medium>
Coverage: <reviewed scope; omissions>
Checks: <your commands/actions, version, results; others' results separately>
```

List findings by descending severity:

```text
### N. <issue> — path/to/file:line
- severity: <blocker|high|medium|low>
- verdict: <CONFIRMED|PLAUSIBLE>
- failure_scenario: <conditions and steps → expected → actual or predicted>
- evidence: <code, commands, output; missing confirmation>
- impact: <affected users or behavior>
- recommendation: <minimal fix direction, without editing>
```

If none, state “No findings” within the declared scope. Always include
`★ Insight ───` with:

- **Coverage:** inspected entities, paths, and processes; omissions and reasons.
- **Observations:** specific location, scenario, consequence, evidence or labeled
  hypothesis, verification criterion, and direction for a separate task. Try to
  disprove these as well. Check existing and rejected tasks; revisit only with
  new evidence.

If there are no useful observations, say so and retain coverage. Do not pad the
section with architecture summaries or invented issues. Insight does not authorize
additional implementation and is excluded from finding counts. `fix-review`
processes its observations. Write backlog entries only under project policy
or user instruction.

End with material limitations, residual risk, and `CONFIRMED N · PLAUSIBLE N`.
Do not describe incomplete coverage as a complete review with no findings.
