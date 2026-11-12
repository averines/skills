# Chain: assess, then plan changes

Use for refactoring, redesign, migration, or other changes to an existing
solution. Read [Six Thinking Hats](six-hats.md) and
[Dreamer / Realist / Critic](disney.md). Follow both methods with the changes below.

Report structure:

```text
Assessment and rework plan: <subject>
Scope: <inspected material>
Goal: <requested change>
Stage 1 — White, Red, Black, Yellow, Green, Blue assessment
Stage 2 — Dreamer, Realist, Critic
Final plan
```

## Stage 1 — Assess the current solution

Use all six hats. In Blue, summarize the assessment and properties to preserve.
Do not prescribe fixes yet. Record Green options for Stage 2.

Pass these results to Stage 2 explicitly:

| Source | Recipient | Required input |
| --- | --- | --- |
| White | Realist | Actual structure, dependencies, and test status |
| Yellow | Every role | Properties to preserve; explain any step that would lose one |
| Black | Realist and Critic | Every confirmed High finding; address it or defer it explicitly with a reason |
| Green | Dreamer | Options to explore |

Keep Black hypotheses as verification steps. Do not promote them to confirmed
defects or treat them as authorization for more work.

## Stage 2 — Plan the changes

- **Dreamer:** explore an improved outcome that addresses confirmed High findings.
  Treat the current implementation as changeable.
- **Realist:** plan the transition from White's actual state while preserving
  Yellow's useful properties. Include change order, any parallel operation,
  and rollback points.
- **Critic:** check whether the plan resolves, misses, or reintroduces Black
  findings. Also check risks created by the transition, including temporary
  failures, data migration, and regressions in preserved behavior.

## Final plan

Produce one final synthesis for both stages:

1. Recommend full or partial rework, a prototype first, or no change now.
2. Map every confirmed High finding to a plan step or a reason for deferral.
3. Give ordered steps. Mark the smallest first release and rollback points.
4. State which properties are preserved and how.
5. State the first action and decisions only the user can make.
6. List useful deferred ideas as optional later work.

Keep the synthesis short enough to read on one screen.
In brief mode, show only Blue's assessment and Final plan.
