# Output Contracts

Use these compact forms to avoid verbose preambles.

## Preflight

```markdown
Token Triage
- Budget mode:
- Need-to-know context:
- Cheap first actions:
- Do not read/open:
- Escalation trigger:
- Answer budget:
```

## Token-Spend Receipt

Use after meaningful exploration, especially when the user asked to save cost.

```markdown
Token-spend receipt:
- Read:
- Skipped:
- Reused:
- Escalated:
```

## Context Capsule

Use when compressing a long chat, repo scan, document, or handoff.

```markdown
Context capsule
- Objective:
- Current state:
- Key facts:
- Decisions:
- Constraints:
- Open questions:
- Source anchors:
- Next cheapest actions:
```

## Bounded Subagent Prompt

Use before spawning another agent.

```markdown
Task:
Relevant context:
Read only:
Do not inspect:
Return:
Stop when:
```

## Minimal Final Answer

For low-risk tasks:

```markdown
Done. Changed X so Y now works.
Verified with Z.
```

For reviews:

```markdown
Findings:
- [severity] file:line - issue and impact.

Residual risk:
- What was not checked.
```
