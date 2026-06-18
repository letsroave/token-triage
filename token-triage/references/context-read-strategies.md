# Context Read Strategies

Use these patterns to reduce context spend while preserving evidence quality.

## Map First

Start with low-cost inventory:

```bash
pwd
rg --files
git status --short
rg "error text|symbol|route|component|function"
```

Prefer file lists, filenames, imports, and symbol names before opening whole files. Read manifests and configs only when they explain execution, dependencies, or test commands.

## Grep First

Search for exact user-provided terms first: error messages, function names, route paths, UI labels, database fields, and config keys. Then broaden only if the exact search fails.

Good sequence:

1. exact phrase;
2. identifier without punctuation;
3. related type/interface/test name;
4. directory-level exploration.

## Slice Reads

Open only the relevant region when possible:

```bash
sed -n '40,140p' path/to/file
nl -ba path/to/file | sed -n '40,140p'
rg -n "functionName|className" path/to/file
```

Read the whole file when it is small, dense, or the surrounding structure matters. Avoid whole-file reads for long generated files, snapshots, lockfiles, logs, vendored code, bundled assets, and minified output.

## Progressive Widening

Use this order for code tasks:

1. User-named files or failing output.
2. Tests around the behavior.
3. Direct implementation symbols.
4. Callers and entrypoints.
5. Shared helpers or framework glue.
6. Broader architecture docs.

Stop widening when the next action is justified by evidence already gathered.

## Summarize Once

For long docs, chats, logs, or transcripts:

- create a compact capsule with objective, decisions, constraints, entities, unresolved questions, and source anchors;
- reuse the capsule instead of rereading the raw material;
- keep raw excerpts only for legally, technically, or semantically precise claims.

## Tool Call Discipline

Batch independent file reads. Avoid repeated tool calls that differ only by small path changes when one targeted search would find all candidates. Before web browsing, ask whether the fact is current, niche, source-sensitive, or high stakes; otherwise prefer local artifacts and model knowledge.
