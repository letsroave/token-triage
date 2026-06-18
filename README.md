# Token Triage

![Token Triage banner](assets/token-triage-banner.svg)

**Token Triage** is a Claude Code plugin and portable agent skill that helps AI agents spend fewer tokens before expensive work.

Most agent waste comes from reading too many files, reopening the same context, spawning vague subagents, browsing before checking local truth, and writing broad summaries when the user needed a small decision. Token Triage gives agents a cheap preflight routine so they inspect less, read smarter, summarize once, and escalate only when more context is truly justified.

## Install For Users

### Claude Code Marketplace Install

Add the LetsRoave marketplace:

```bash
claude plugin marketplace add https://github.com/letsroave/token-triage
```

Install the plugin:

```bash
claude plugin install token-triage@letsroave
```

Then use it in Claude Code:

```text
Use $token-triage before reviewing this repository.
```

### Claude Code One-Session Test

If you only want to test the plugin for one session:

```bash
claude --plugin-dir plugins/token-triage
```

### Claude.ai Skill Upload Fallback

Claude.ai users can download the standalone skill ZIP from releases:

```text
https://github.com/letsroave/token-triage/releases/latest/download/token-triage-skill.zip
```

Or package the standalone skill folder manually:

```text
plugins/token-triage/skills/token-triage
```

The skill description is kept under Claude.ai's 200-character upload limit.

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

The skill guides the agent to:

- classify task complexity and risk;
- choose `micro`, `focused`, `standard`, or `deep` budget mode;
- map and grep before opening large files;
- read the smallest evidence-bearing snippets first;
- maintain a context ledger to avoid repeated reads;
- create reusable context capsules for long docs, chats, logs, and handoffs;
- avoid broad subagent fan-out unless each subtask is bounded;
- calculate tokens and dollars saved after triage;
- preserve correctness for high-stakes tasks instead of saving tokens recklessly.

## Plugin Layout

```text
.
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── token-triage/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── README.md
│       ├── LICENSE
│       ├── assets/
│       │   └── token-triage-banner.svg
│       └── skills/
│           └── token-triage/
│               ├── SKILL.md
│               ├── agents/openai.yaml
│               ├── references/
│               └── scripts/
└── assets/
    └── token-triage-banner.svg
```

## Context Estimator

Estimate context before reading:

```bash
python plugins/token-triage/skills/token-triage/scripts/estimate_context.py .
python plugins/token-triage/skills/token-triage/scripts/estimate_context.py src tests --top 20
cat notes.md | python plugins/token-triage/skills/token-triage/scripts/estimate_context.py --stdin
```

It ignores common noise folders such as `.git`, `node_modules`, `build`, `dist`, caches, and binary assets.

## Savings Calculator

Prove whether triage actually saved context:

```bash
python plugins/token-triage/skills/token-triage/scripts/calculate_savings.py \
  --baseline-tokens 50000 \
  --actual-tokens 12000 \
  --baseline-output-tokens 4000 \
  --actual-output-tokens 1200 \
  --runs 20 \
  --input-price-per-1m 3 \
  --output-price-per-1m 15
```

Example output:

```text
Token savings calculator
- Baseline input tokens: 50,000
- Triaged input tokens: 12,000
- Baseline output tokens: 4,000
- Triaged output tokens: 1,200
- Saved per run: 40,800 tokens (75.6%)
- Saved across 20 run(s): 816,000 tokens
- Baseline cost per run: $0.210000
- Triaged cost per run: $0.054000
- Cost saved per run: $0.156000
- Cost saved across 20 run(s): $3.120000
- Input/output delta: 38,000 input, 2,800 output
```

## Detailed Working Check

| Check | Command | Expected result |
| --- | --- | --- |
| Marketplace schema | `claude plugin validate .claude-plugin/marketplace.json` | validation passes |
| Plugin schema | `claude plugin validate plugins/token-triage` | validation passes |
| Skill schema | `python /path/to/quick_validate.py plugins/token-triage/skills/token-triage` | `Skill is valid!` |
| Python syntax | `python -m py_compile plugins/token-triage/skills/token-triage/scripts/*.py` | exits `0` |
| Folder estimation | `python plugins/token-triage/skills/token-triage/scripts/estimate_context.py plugins/token-triage/skills/token-triage --top 8` | ranks package files and suggests targeted reads |
| Stdin estimation | `printf 'compact context check\n' \| python plugins/token-triage/skills/token-triage/scripts/estimate_context.py --stdin` | reports estimated tokens |
| Manual savings | `python plugins/token-triage/skills/token-triage/scripts/calculate_savings.py --baseline-tokens 50000 --actual-tokens 12000 --baseline-output-tokens 4000 --actual-output-tokens 1200 --runs 20 --input-price-per-1m 3 --output-price-per-1m 15` | reports 816,000 tokens and $3.12 saved across 20 runs |
| Overspend detection | `python plugins/token-triage/skills/token-triage/scripts/calculate_savings.py --baseline-tokens 1000 --actual-tokens 1500 --input-price-per-1m 3` | reports extra tokens and extra cost |

## Official Claude Directory

This repo is structured for marketplace distribution now. The next credibility step is submission to Anthropic's plugin directory using:

```text
https://clau.de/plugin-directory-submission
```

Submission requires review by Anthropic and may require publisher/contact details. The plugin metadata is already in `plugins/token-triage/.claude-plugin/plugin.json`, and the marketplace entry is in `.claude-plugin/marketplace.json`.

## Design Principles

- **Spend context like money.** Every large read should buy a fact, decision, or next action.
- **Map before reading.** File lists, symbol search, manifests, and test names are cheaper than full files.
- **Summarize once.** Long context should become a reusable capsule, not repeated raw input.
- **Escalate honestly.** If safety, security, finance, law, medicine, or production correctness requires more evidence, spend the tokens and say why.
- **Keep the skill portable.** No vendor lock-in, no API dependency, no required package manager.

## License

MIT. See [plugins/token-triage/LICENSE](plugins/token-triage/LICENSE).
