# Budget Modes

Use these modes to make context spend explicit.

## Micro

Use when the answer is direct or the user names exact material.

- Exploration: none or one targeted read/search.
- Tool calls: 0-2.
- Output: concise answer or tiny patch summary.
- Escalate when the named input is insufficient or the task is high stakes.

## Focused

Use for narrow coding, debugging, explanation, or editing.

- Exploration: map-first, grep-first, then 1-5 relevant snippets/files.
- Tool calls: batch independent reads.
- Output: focused implementation notes and verification.
- Escalate when searches find multiple plausible subsystems or test output contradicts the hypothesis.

## Standard

Use for moderate feature work, subsystem review, or unfamiliar code.

- Exploration: file map, manifests, relevant tests, entrypoints, and core implementation.
- Tool calls: maintain a context ledger and avoid rereads.
- Output: concise but complete plan/change summary.
- Escalate when cross-cutting contracts, migrations, auth, data loss, or production behavior are involved.

## Deep

Use for high-risk or broad tasks.

- Exploration: wider repo/docs/source review, tests, external verification where needed.
- Tool calls: define a question for each expensive action or subagent.
- Output: evidence-backed findings, risks, and next steps.
- Escalate to the user before very large reads, long-running jobs, paid APIs, external writes, or multi-agent fan-out.

## Escalation Template

```markdown
Escalation needed:
- Current evidence:
- Missing fact:
- Cheapest reliable next step:
- Estimated cost:
- Why it matters:
```

## Hard Token Budgets

When the user gives a numeric budget, treat it as a cap for exploration unless they specify total response budget.

- Reserve 25-35% for synthesis and final answer.
- Spend the first 10% on mapping, not reading.
- Stop and summarize when the next read would exceed the cap.
- Prefer one high-value source over several partially relevant sources.
- If correctness requires exceeding the cap, ask for escalation and explain the smallest useful increase.
