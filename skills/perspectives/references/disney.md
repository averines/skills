# Dreamer / Realist / Critic

Use this order: **Dreamer → Realist → Critic → Final plan**.

Report structure:

```text
Dreamer / Realist / Critic: <idea>
Input: <user's goal, one or two sentences>
Dreamer — Ideal outcome
Realist — Implementation plan
Critic — Risks in the plan
Final plan
```

## Dreamer — Ideal outcome

Describe the desired user outcome, useful distinguishing features, and
potential future scope. Define success through observable user results.

Preserve explicit constraints and non-goals. Treat the current implementation
as changeable. Explore options beyond the initial request when useful, but
label them as optional; they do not expand authorization.

Do not discuss feasibility, effort, or risks in this role.

## Realist — Implementation plan

Treat Dreamer ideas as options, not approved requirements.

Read relevant code and configuration if the plan affects an existing project.
Use the actual project context and reuse existing components.

Specify:

- Scope for the first release and later phases.
- Ordered implementation steps, naming relevant components and interfaces.
- What to reuse and what to create.
- Rough effort per step, such as S/M/L, where supportable.
- The smallest end-to-end version that demonstrates the outcome.

Make steps specific enough to execute. Explain how to implement the idea;
leave criticism of the idea to Critic.

## Critic — Risks in the plan

Check the implementation plan for:

- Technical and integration failures or hidden complexity.
- Unsupported assumptions about users, data, load, or external services.
- Missing edge cases, migrations, operations, or relevant legal/compliance needs.
- Underestimated effort.
- Evidence that would invalidate the approach.

For each risk, state the evidence or assumption and the simplest useful way
to check it: an experiment, prototype, or question. Do not invent probability
or effort estimates. Do not add criticism without a verification or mitigation
step. Leave the decision on the idea's value to Final plan.

## Optional second loop

Use this only if Critic identifies a blocker that invalidates Realist's plan.
Ordinary risks are not enough.

Run at most one extra loop:

1. Dreamer adjusts the outcome in two or three points.
2. Realist updates only the affected steps.

Then produce Final plan.

## Final plan

Keep this section short enough to read on one screen:

1. Recommend `go`, `go-with-changes`, `needs-a-spike-first` (prototype first),
   or `no-go`.
   Give a two-sentence rationale that accounts for all three roles.
2. Give the ordered plan with Critic's verification and mitigation steps.
   Mark the smallest first release.
3. State the single first action.
4. List decisions only the user can make.
5. List useful deferred ideas as optional later work.
