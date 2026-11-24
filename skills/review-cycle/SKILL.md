---
name: review-cycle
license: MIT
description: Run a bounded review, verification, and correction cycle for an explicit Git commit or range. Use on request or after a substantive commit when the task and project rules allow review. Fixes and fix commits require authorization.
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
commit, use its exact hash without asking for it again. Resolve the target as specified by code-review. Pass the requested form,
resolved base and tip, comparison method, selected merge parent when
applicable, and included commits between stages. Ask if ambiguous;
do not select all unpushed history automatically. Working trees, staged changes,
and individual files are not targets. Outside Git, state the limitation and
stop. Do not create an initial commit just to start this workflow.

An explicit request to run this cycle authorizes necessary separate fix commits
unless the task or project rules prohibit them. For an automatic cycle, check
that the task or project rules authorize commits. If commits are prohibited,
leave any verified fixes uncommitted. If fixes remain uncommitted, report the
cycle as incomplete. Do not start another round on the original target as a
substitute for a fix commit.
Preserve user changes. Do not rewrite history or push.

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
   full pass, each round covers the entire task at `high`. Always inspect the
   complete target. If independent delegation is available and authorized,
   delegate read-only review to a reviewer without the author's conversation
   history. Supply the target, original requirements, decisions already agreed, and
   environment prerequisites, without self-assessment or desired findings.
   The reviewer must not delegate again. If delegation is unavailable, not
   authorized, or cannot provide separate context, review the target yourself
   in a separate pass. State that it is not independent. This fallback can
   support completion with limitations only when independent review is optional.
   Author and reviewer must not edit the same copy at the same time.
2. **Coverage.** Check what the reviewer inspected and which version they ran.
   For interactive changes, the reviewer must run the affected workflow in its
   target runtime as required by code-review. This does not always require a
   browser. Keep author/CI results separate. Ask the reviewer to complete any
   available but omitted scenarios or missing Insight block in the same round.
   An author's supplemental pass does not satisfy required independent coverage.
   For unavailable runs, record the obstacle and unverified outcome. Do not
   report incomplete coverage as a complete review with no findings or treat
   it as evidence of a defect.
3. **Process findings.** Use fix-review to check each finding instead of accepting
   the report as proof. Use its six classes. Track each finding's status, edits,
   evidence, significant remaining defects, and checks as well as counts. Carry
   open defects across rounds, including ones marked `repeat` or `deferred`.
   Propose separate tasks for out-of-scope Insight observations; do not implement them.
4. **Fixes.** After required pre-commit checks pass, create a separate commit if
   authorized and if the exact patch can be safely isolated under fix-review.
   Follow project commit conventions and record the hash and verified version.
   Without a fix commit, do not start another round on those edits. New regression
   tests must detect the original failure. Continue this cycle after a fix commit.
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

1. **A completion condition is unmet:** a material confirmed defect is still open,
   required coverage of the current round is incomplete (including independence
   when required), a required check failed or is unavailable, edits remain
   uncommitted, or a user decision is needed. Do what is possible in scope.
   If the condition remains unmet, stop as “incomplete” and name the reason and
   the next action.
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
   is not authorized, use the fallback rule from step 1 of “Each round”.
7. **Both limits exhausted; a new substantive fix is unreviewed:** stop as
   “limit reached; cycle incomplete”. List changes, risks, and the required
   decision. Do not continue indefinitely or describe exhaustion as success.

A substantive fix needing review stays open until the next applicable pass under
rules 5–7 succeeds. If all required conditions are met, use “complete with
limitations” for an optional check with unverified outcomes or for the optional
independent-review fallback. State the unverified outcome or lack of
independence. An unavailable check alone does not establish a defect. The cycle
status does not authorize release.

## Report

For each round:

```text
Round N (<exact target>): defect N · hardening N · nit N · rejected N · repeat N · deferred N → <fix hash | —>
```

Finish with original and final targets, all fix commits, actual checks, remaining
finding states, and one status: `complete`, `complete with limitations`, or
`incomplete: <reason>`. Include material limitations, residual risk, and useful
“Proposed tasks”. Write backlog entries only under project policy or user instruction.
