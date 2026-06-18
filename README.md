# Token Triage

![Token Triage banner](assets/token-triage-banner.svg)

**Token Triage** is a portable AI-agent skill that helps Claude, Codex, and similar coding agents spend fewer tokens before doing expensive work.

Most agent waste does not come from one long answer. It comes from reading too many files, reopening the same context, spawning vague subagents, browsing before checking local truth, and writing broad summaries when the user needed a small decision. Token Triage gives agents a cheap preflight routine so they inspect less, read smarter, summarize once, and escalate only when more context is truly justified.

## What It Does

Token Triage teaches an agent to produce a compact preflight contract before expensive work:

```markdown
Token Triage
- Budget mode:
- Need-to-know context:
- Cheap first actions:
- Do not read/open:
- Escalation trigger:
- Answer budget:
```

The skill then guides the agent through a practical cost-saving workflow:

- classify task complexity and risk;
- choose `micro`, `focused`, `standard`, or `deep` budget mode;
- map and grep before opening large files;
- read the smallest evidence-bearing snippets first;
- maintain a context ledger to avoid repeated reads;
- create reusable context capsules for long docs, chats, logs, and handoffs;
- avoid broad subagent fan-out unless each subtask is bounded;
- preserve correctness for high-stakes tasks instead of saving tokens recklessly.

## Why It Is Useful

Agents often default to "read everything, then think." That works, but it is expensive.

Token Triage flips the loop:

1. Decide what evidence is actually needed.
2. Search cheaply for where that evidence lives.
3. Read only the smallest useful source.
4. Record what was learned.
5. Escalate only when the next context spend has a clear purpose.

This makes it especially useful for:

- large repositories;
- long chats and handoffs;
- bug fixing with unknown scope;
- code review with minimal context;
- planning under a token budget;
- teams using paid agentic coding tools;
- users who want lower LLM costs without losing reliability.

## Install

Copy the installable skill folder into your agent's skill directory:

```bash
cp -R token-triage ~/.codex/skills/token-triage
```

For Claude or other agents, copy `token-triage/SKILL.md` into the equivalent skill, project-instruction, or custom-agent workflow location. The skill is plain Markdown plus one dependency-free Python helper, so it does not require a Codex-only runtime.

## Usage

Invoke it explicitly:

```text
Use $token-triage before reviewing this repository.
```

```text
Use $token-triage to plan this feature, but keep exploration under 5k tokens.
```

```text
Use $token-triage to summarize this long handoff into a reusable context capsule.
```

Or bake it into an agent's default behavior for tasks involving repo exploration, long documents, broad debugging, multi-agent work, or web research.

## Context Estimator

The package includes a small utility for estimating context before reading:

```bash
python token-triage/scripts/estimate_context.py .
python token-triage/scripts/estimate_context.py src tests --top 20
cat notes.md | python token-triage/scripts/estimate_context.py --stdin
python token-triage/scripts/estimate_context.py . --include "*.py" --exclude snapshots
```

It ignores common noise folders such as `.git`, `node_modules`, `build`, `dist`, caches, and binary assets. The output ranks the largest files and suggests whether to read directly, grep first, summarize, or narrow scope.

Example output:

```text
Context estimate
- Files: 6
- Bytes: 17,122
- Estimated tokens: 4,283
- Read plan: read targeted files or snippets; avoid rereading

Top 6 largest files:
     1,565 tokens  token-triage/scripts/estimate_context.py
     1,342 tokens  token-triage/SKILL.md
```

## Package Layout

```text
token-triage/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── budget-modes.md
│   ├── context-read-strategies.md
│   └── output-contracts.md
└── scripts/
    └── estimate_context.py
```

## Design Principles

- **Spend context like money.** Every large read should buy a fact, decision, or next action.
- **Map before reading.** File lists, symbol search, manifests, and test names are cheaper than full files.
- **Summarize once.** Long context should become a reusable capsule, not repeated raw input.
- **Escalate honestly.** If safety, security, finance, law, medicine, or production correctness requires more evidence, spend the tokens and say why.
- **Keep the skill portable.** No vendor lock-in, no API dependency, no required package manager.

## Validation

The skill was checked with:

```bash
python -m py_compile token-triage/scripts/estimate_context.py
python token-triage/scripts/estimate_context.py token-triage --top 6
python /path/to/quick_validate.py token-triage
```

If your validator's Python environment does not include `PyYAML`, install it into a temporary local dependency directory and set `PYTHONPATH` for that one validation run.

## Status

This is a v1 portable skill package. It is intentionally small enough to be useful as default agent behavior, but structured enough to handle large repositories, long handoffs, and budget-constrained workflows.
