---
name: token-triage
description: Token and context cost governor for AI agents. Use before expensive work, repo exploration, long document analysis, multi-agent coordination, web research, large file reads, broad code review, feature planning, debugging with unknown scope, summarization, or any task where the agent should inspect less, avoid repeated reads, choose the cheapest adequate workflow, and escalate only when more context is justified.
---

# Token Triage

Use this skill as a preflight before spending substantial context, tool calls, wall time, or money. The goal is not to be terse at all costs; it is to buy the right amount of context for the task and no more.

## Quick Start

Before exploring or answering, produce this compact contract:

```markdown
Token Triage
- Budget mode:
- Need-to-know context:
- Cheap first actions:
- Do not read/open:
- Escalation trigger:
- Answer budget:
```

Then follow the contract. If the task is tiny, keep the contract to one or two lines or fold it into your working notes.

## Budget Modes

Choose the cheapest mode that can still satisfy the request:

| Mode | Use for | Default behavior |
| --- | --- | --- |
| `micro` | Direct answers, tiny edits, known files, simple transformations | No broad search. Read only named inputs. Final answer under 150 words unless asked otherwise. |
| `focused` | Small bug fixes, local explanations, narrow repo questions | Map with `rg --files`, then inspect only likely files and symbols. Avoid full-file reads when targeted snippets work. |
| `standard` | Moderate features, unfamiliar areas, code review of a subsystem | Build a file map, identify entrypoints, read in slices, maintain a context ledger. |
| `deep` | Architecture, security, high-risk correctness, migrations, broad audits | Allow wider search and verification, but checkpoint before large logs, generated files, or multi-agent fan-out. |

Read `references/budget-modes.md` when the task needs explicit thresholds, escalation rules, or a user-imposed token budget.

## Workflow

1. **Classify the task.** Identify outcome, risk, likely context sources, and whether the user asked for implementation, planning, review, or explanation.
2. **Pick a budget mode.** Default to `focused` for code tasks unless the user names exact files (`micro`) or requests broad analysis (`standard`/`deep`).
3. **Map before reading.** Prefer cheap inventory commands: `pwd`, `rg --files`, `rg "symbol|error|route"`, `git status --short`, manifests, tests, and directory names.
4. **Read by evidence value.** Open the smallest source that can answer the next question: symbol definitions, call sites, test failures, configs, or docs sections.
5. **Keep a context ledger.** Track what was read and what it proved. Do not reread the same file unless looking for a new target.
6. **Escalate deliberately.** Before high-cost steps, state why the current context is insufficient and what the next read/tool call should prove.
7. **Spend output tokens intentionally.** Match response length to the task. Prefer summaries with links, commands, or exact next steps over broad narration.

For detailed read tactics, use `references/context-read-strategies.md`. For reusable response shapes, use `references/output-contracts.md`.

## Savings Levers

Apply these in order:

1. **Narrow the question.** Convert broad goals into the smallest next decision or edit.
2. **Shrink the read set.** Use names, errors, symbols, manifests, and tests to target context.
3. **Cache the understanding.** Create a context capsule for large material that may be reused.
4. **Avoid fan-out.** Spawn agents or run broad searches only after defining bounded questions.
5. **Limit the answer.** Match final detail to the user-visible need and link to artifacts instead of restating them.

## Context Ledger

Maintain a short ledger in working notes for non-trivial tasks:

```markdown
Context ledger
- Read: `path/or/source` -> learned X; supports Y.
- Skipped: `path/or/source` -> reason.
- Open question: Z; cheapest next check is A.
```

The ledger prevents circular exploration and makes handoffs cheaper.

## Estimating Context

Use `scripts/estimate_context.py` when a directory, file set, pasted text, or transcript may be large.

Examples:

```bash
python scripts/estimate_context.py .
python scripts/estimate_context.py src tests --top 20
cat notes.md | python scripts/estimate_context.py --stdin
python scripts/estimate_context.py . --include "*.py" --exclude "snapshots"
```

Use the estimate to decide whether to read directly, search first, summarize, or ask for a narrower scope.

## Safety And Accuracy Guardrail

Never save tokens by skipping required verification for current facts, legal, medical, financial, security, safety, compliance, or production-impacting claims. In those cases, escalate to authoritative sources, tests, or explicit uncertainty.

## Anti-Patterns

- Reading every file before forming a hypothesis.
- Opening generated files, lockfiles, build outputs, logs, or vendored code without a concrete reason.
- Spawning subagents before defining a bounded question for each.
- Summarizing the same material repeatedly instead of creating a reusable capsule.
- Producing long plans when the user needs a small edit or a decision.
- Treating token reduction as more important than correctness, safety, or user intent.
