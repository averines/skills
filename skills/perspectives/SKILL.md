---
name: perspectives
license: MIT
description: Analyze designs, architecture, documents, ideas, and plans using Six Thinking Hats, Dreamer / Realist / Critic, or diagnosis followed by a rework plan. Use for distinct viewpoints, tradeoffs, brainstorming, or an explicit request for either method. Does not replace defect-focused code review.
metadata:
  author: averines
---

# Perspectives

Analyze one perspective at a time, in the order defined by the selected method.
Keep each role's assessment separate until synthesis. Roles do not provide
independent review or prove correctness. No specific agent, plugin, command
interface, or delegation tool is required.

## Scope and evidence

- Follow the user's scope and project rules. Analysis does not authorize edits,
  commits, deployment, or additional implementation.
- Distinguish observations, hypotheses, and confirmed causes. Treat Red-hat
  impressions as subjective. Support Black-hat findings with evidence or label
  them as hypotheses. Do not turn impressions into defects during synthesis.
- Read available source material before assessing it. Check current external
  facts when needed and tools permit. Report checks you could not perform.

## 1. Select the mode

Follow the user's explicit choice. Otherwise select by the requested outcome:

| Mode | Use when | Required reading |
| --- | --- | --- |
| `six-hats` | Assess existing code, a PR/diff, architecture, configuration, or a document | [Six Thinking Hats](references/six-hats.md) |
| `disney` | Develop a new idea, feature, integration, or tool into a plan | [Dreamer / Realist / Critic](references/disney.md) |
| `chain` | Assess an existing solution, then plan its refactoring, redesign, or migration | [Chain](references/chain.md), [Six Thinking Hats](references/six-hats.md), and [Dreamer / Realist / Critic](references/disney.md) |

For analysis alone, use `six-hats`. Ask one short question only if the mode is
still unclear and the answer would materially change the deliverable.

## 2. State the scope

Before using the first perspective:

1. Identify the exact files, directory, diff, PR, or written idea to assess.
   Do not expand the scope to the whole project without instruction.
2. For code, read the actual files and relevant Git diff/history.
   Do not infer behavior from filenames or memory.
3. For large inputs, prioritize material relevant to the user's goal. State
   what you sampled or omitted. Ask about scope only when necessary.
4. State the inspected scope at the top of the report.

## 3. Apply the method

- Use every required role, in order, with a labeled section for each.
- Keep risk assessment in its role and benefits in theirs. Keep feasibility
  and effort estimates out of Dreamer. Combine perspectives only in synthesis.
- Give each role a full assessment within its purpose. Do not soften criticism
  with praise or restrict creative options with objections from a later role.
- Support factual claims with source links, line numbers, or symbols when
  available. Do not invent sources, quotes, locations, or test results.
- Match detail to the scope. Do not invent findings, benefits, or alternatives
  to fill a quota. State when the material supports none.

## 4. Report the result

Use the structure in the selected reference. Include its required synthesis
(Blue or Final plan), with High / Medium / Low priorities, concrete actions,
user decisions, and coverage limits. Keep it short enough to read on one screen.

Use the user's language; preserve identifiers, paths, and technical terms.
Deliver in chat unless the user requested another format.

By default, report every role. If the user requests a brief answer, consider
all required roles but show only the synthesis specified by the reference.
Retain evidence, limitations, and actions. Do not expose private reasoning
or claim that role changes provide independent verification.
