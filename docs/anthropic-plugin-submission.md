# Anthropic Plugin Directory Submission Notes

Use this when submitting Token Triage to the official Claude plugin directory.

## Submission URL

```text
https://clau.de/plugin-directory-submission
```

## Plugin Metadata

- Plugin name: `token-triage`
- Marketplace name: `letsroave`
- Repository: `https://github.com/letsroave/token-triage`
- Homepage: `https://github.com/letsroave/token-triage`
- Category: `productivity`
- License: `MIT`
- Publisher: `letsroave`
- Plugin path in repo: `plugins/token-triage`
- Manifest path: `plugins/token-triage/.claude-plugin/plugin.json`

## Short Description

Token/context cost governor for AI agents. Read less, estimate savings, and choose cheaper workflows before expensive work.

## Longer Description

Token Triage helps Claude Code users reduce token and context costs before expensive agent work. It adds a preflight workflow for choosing a budget mode, mapping before reading, avoiding duplicate context reads, creating reusable context capsules, and calculating tokens or dollars saved after triage.

## User Install

```bash
claude plugin marketplace add https://github.com/letsroave/token-triage
claude plugin install token-triage@letsroave
```

## Validation Evidence

Run from the repository root:

```bash
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate plugins/token-triage
python -m py_compile plugins/token-triage/skills/token-triage/scripts/estimate_context.py plugins/token-triage/skills/token-triage/scripts/calculate_savings.py
python plugins/token-triage/skills/token-triage/scripts/calculate_savings.py --baseline-tokens 50000 --actual-tokens 12000 --runs 20 --input-price-per-1m 3 --output-price-per-1m 15
```
