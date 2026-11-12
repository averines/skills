---
name: review-cycle
license: MIT
description: Run a bounded review, verification, and correction cycle for an explicit Git commit or range. Use after a substantive commit when the task and project rules allow review and any required fix commits.
compatibility: Requires Git, an explicit commit or range, and the code-review and fix-review skills. Independent delegation is optional; runtime checks depend on the project.
metadata:
  author: averines
---

# Review cycle

Read code-review and fix-review before starting. If either is unavailable, name
the stage that cannot run. Do not start a second cycle while another process
manages the same review. Keep your own fix commits in the current cycle.
Respond in the user's language; preserve identifiers and classification labels.

## Target and authorization

Require an explicitly selected Git commit or range. After your own authorized
commit, use its exact hash without asking for it again. Resolve hashes, base,
tip, root, and merge handling as specified by code-review. Ask if ambiguous;
do not select all unpushed history automatically. Working trees, staged changes,
and individual files are not targets. Outside Git, state the limitation and
stop. Do not create an initial commit just to start this workflow.

An explicit request to run this cycle authorizes necessary separate fix commits
unless the task or project rules prohibit them. For an automatic cycle, check
that the task or project rules authorize commits. If commits are prohibited,
leave verified edits uncommitted. Report that you did not commit the fixes or
review a resulting fix commit. Preserve user changes. Do not rewrite history or push.

Do not start if the user excluded review or another process already manages it.
Changes limited to status text or formatting may not need a full cycle if their
meaning and behavior are unchanged. Assess effects before excluding generated code,
tests, CI, configuration, resources, or operational documentation. A previous
clean review does not exempt new code. Do not repeat an unchanged verified target.

Record the original comparison base and included commits before fixing anything.
For a root, use the empty tree as the comparison base. A later full pass must
cover “from <root-hash>, inclusive, through <tip-hash>” and empty-tree-to-tip
comparison, not `root..tip`. For merges, retain the agreed comparison base.
Do not exclude intermediate commits merely because they are labeled docs. If unrelated
work enters the branch, clarify boundaries or use a separate authorized copy;
do not silently include it in the task.

## Each round

1. **Review.** First review the original target at `high`; then review fix commits
   at `medium`, retaining task context and previous decisions. In the second
   full pass, both rounds cover the entire task at `high`. Always inspect the
   complete target. If independent delegation is available and authorized,
   delegate read-only review to a reviewer without the author's conversation
   history. Supply the target, original requirements, decisions already agreed, and
   environment prerequisites, without self-assessment or desired findings.
   The reviewer must not delegate again. If delegation is unavailable, not
   authorized, or cannot provide separate context, review the target yourself
   in a separate pass. State that this pass is not independent. Author and
   reviewer must not edit the same copy at the same time.
2. **Coverage.** Check what the reviewer inspected and which version they ran.
   For interactive changes, the reviewer must run the affected workflow in its
   target runtime as required by code-review. This does not always require a
   browser. Keep author/CI results separate. Ask the reviewer to complete any
   available but omitted scenarios or missing Insight block in the same round.
   For unavailable runs, record the obstacle and unverified outcome. Do not
   report incomplete coverage as a complete review with no findings or treat
   it as evidence of a defect.
3. **Process findings.** Use fix-review to check each finding instead of accepting
   the report as proof. Use its six classes. Track each finding's status, edits,
   evidence, significant remaining defects, and checks as well as counts.
   Propose separate tasks for out-of-scope Insight observations; do not implement them.
4. **Fixes.** Run relevant project checks. If authorized, create a separate commit
   containing only related fixes, following project commit conventions. Record
   its hash and verified version. New regression tests must detect the original
   failure. A fix commit continues this cycle; it does not trigger a nested one.
5. **Decision.** Apply the ordered rules below, not just the `defect` count.

## Decision order and limits

Use project or agreed-plan limits when specified. Otherwise allow at most three
rounds in the first pass and, if needed, one full second pass of at most two
rounds. The limits control effort; they do not establish that review is complete.
One round includes a review and processing its findings. Adding missing parts
to the same report does not start a new round. Number rounds and do not reset
the counter after fix commits.

First use the fix diff and affected workflows to decide whether the fixes need
review. Do not decide from `defect`/`hardening`/`nit` labels alone. Changes to
behavior, contracts, executable configuration, or required checks need review.
Purely cosmetic fixes may finish without another review after you check their
effects. Then apply these rules in order:

1. **Material confirmed defect, failed required check, or required user decision
   remains:** resolve what is possible in scope. If a decision or environment
   blocks further work, stop as “incomplete” and name the next action. Do not
   declare readiness because an item is `deferred` or a fix was not committed.
2. **Requirements or decisions conflict, or fixes recur:** compare causes and
   behavior. Reversing an earlier change is a reason to investigate, not proof
   of an endless cycle. Restoring a safeguard with evidence is valid. If the
   conflict is resolved, continue with the remaining rules. Otherwise stop as
   “incomplete” and request the user's decision.
3. **No fixes needed:** finish with actual coverage and limits. List confirmed
   deferred items; a material issue from rule 1 cannot pass through this branch.
4. **Fixes verified; their effects require no further review:** finish and state why.
5. **Another round needed; first-pass limit remains:** review fix commits at `medium`.
6. **First pass exhausted; second pass remains; latest fix needs review:** use a
   fresh reviewer for `high` review of the whole task from the original base
   through the latest fix, up to two rounds. Include root when applicable and
   exclude unrelated commits. If no fresh reviewer is available or delegation
   is not authorized, repeat the review yourself. State that the repeated pass
   is not independent and report the remaining risk.
7. **Both limits exhausted; a new substantive fix is unreviewed:** stop as
   “limit reached; cycle incomplete”. List changes, risks, and the required
   decision. Do not continue indefinitely or describe exhaustion as success.

An unavailable check does not establish a defect. If no defect is proven, the
result may be “complete with limitations”. State the unverified scenario; this
status does not authorize release. If project policy requires that check,
use rule 1 instead.

## Report

For each round:

```text
Round N (<exact target>): defect N · hardening N · nit N · rejected N · repeat N · deferred N → <fix hash | —>
```

Finish with original and final targets, all fix commits, actual checks, remaining
finding states, and one status: `complete`, `complete with limitations`, or
`incomplete: <reason>`. Include material limitations, residual risk, and useful
“Proposed tasks”. Write backlog entries only under project policy or user instruction.
