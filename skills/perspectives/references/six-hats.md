# Six Thinking Hats

Use this order: **White → Red → Black → Yellow → Green → Blue**.
Use every role, even when its contribution is brief.

Report structure:

```text
Six Thinking Hats: <subject>
Scope: <inspected material>
White — Facts
Red — Impressions
Black — Risks and problems
Yellow — Strengths and value
Green — Alternatives
Blue — Synthesis and actions
```

## White — Facts

Describe the material without judgment:

- Actual behavior, structure, and size where relevant.
- Dependencies and versions.
- Existing tests, which ran, and what they checked.
- Documented and undocumented behavior.
- Missing information needed for assessment, such as requirements or types.

State what exists. Avoid evaluative descriptions such as "bloated" or "messy".

## Red — Impressions

Give brief, first-person reactions: confusion, friction, concerns about
fragility or maintenance, or features that feel clear and trustworthy.
Label them as subjective. Do not argue their case here.

Check any actionable concern in Black before treating it as a defect.

## Black — Risks and problems

Check concrete failure scenarios. Assess relevant correctness, edge cases,
security, performance, scaling, reliability, concurrency, lifecycle,
maintainability, deployment, migrations, and compatibility.

Start each finding with **[Severity: High/Medium/Low; confirmed/hypothesis]**.
Then give the source location, evidence, scenario, and realistic consequence.
For a hypothesis, add the check needed to confirm it.

Severity does not establish evidence. Keep benefits for Yellow.
Do not list vague concerns without a concrete scenario.

## Yellow — Strengths and value

Identify decisions and properties worth preserving: correct design choices,
reusable parts, extensibility, testability, clear boundaries, or benefits
a rewrite could lose.

For each, name the decision and explain its value. Avoid generic praise.

## Green — Alternatives

Offer distinct useful options: alternative designs, focused refactoring,
ideas from other domains, or changes that test an assumption, such as removing
a layer.

For each option, give its main idea, benefit, and cost. Do not write a full
design here or add equivalent options to fill space.

## Blue — Synthesis and actions

Keep this section short enough to read on one screen:

1. Assess the overall state in two or three sentences.
2. Prioritize Black findings with evidence. Check that proposed changes preserve
   Yellow's useful properties. Keep unverified Red impressions as questions.
3. Give concrete, ordered actions and locations. Include useful Green options.
4. List decisions only the user or team can make.
5. State omitted scope and verification limits.
