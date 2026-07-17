---
name: run-deep-swe
description: Score any AI model on the DeepSWE coding-agent benchmark via the OpenRouter API. Use when the user wants an independent, reproducible coding-agent eval — "run DeepSWE", "benchmark this model on DeepSWE", "score model X on the coding benchmark", "test a model via OpenRouter on DeepSWE", or to verify vendor-reported coding scores. Covers setup, the OpenRouter wiring for mini-swe-agent, single-task / subset / full 113-task runs, and leaderboard submission.
disable-model-invocation: true
---

# Run DeepSWE via OpenRouter

DeepSWE (deepswe.datacurve.ai) is a 113-task Harbor-compatible coding-agent benchmark. It runs via **Pier** (Harbor fork) driving **mini-swe-agent** (model-agnostic). Any model reachable through OpenRouter can be scored.

## Prerequisites — state-check first

```bash
which uv git docker || echo "MISSING: install uv, git, docker"
docker info >/dev/null 2>&1 || echo "MISSING: Docker daemon not running (Pier's default sandbox)"
echo "OPENROUTER_API_KEY set? ${OPENROUTER_API_KEY:+YES}"
```

**Docker must be running** — Pier sandboxes each task in Docker by default (`--env modal` for cloud instead).

Export an `OPENROUTER_API_KEY` for this benchmark in your shell profile (e.g. `~/.zshrc`). A fresh shell should already have `OPENROUTER_API_KEY` available. If it's somehow not set, re-source the shell:

```bash
source ~/.zshrc && echo "key loaded? ${OPENROUTER_API_KEY:+YES}"
```

If still unset, ask the user — never invent a key.

## Setup

```bash
git clone https://github.com/datacurve-ai/deep-swe && cd deep-swe
uv tool install datacurve-pier            # PyPI (preferred)
# or: uv tool install git+https://github.com/datacurve-ai/pier
# pier bundles mini-swe-agent as the --agent driver
```

Run all `pier` commands from inside `deep-swe/`, using relative `-p tasks/...`.

## OpenRouter wiring (the part the docs don't spell out)

mini-swe-agent has a native OpenRouter model class. Both routes below use `OPENROUTER_API_KEY` and the OpenRouter slug (`vendor/model`, e.g. `minimax/minimax-m3`):

**Route A — native OpenRouter class (preferred, hits openrouter.ai/api/v1 directly):**
```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model minimax/minimax-m3 --model-class openrouter
```

**Route B — LiteLLM provider prefix (fallback; same key):**
```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model openrouter/minimax/minimax-m3
```

Notes:
- Slug = the exact OpenRouter slug. Verify it at openrouter.ai/models before running.
- Free/zero-cost models: OpenRouter cost tracking can error. Set `export MSWEA_COST_TRACKING=ignore_errors`.
- Flag spelling can vary by version — confirm with `pier run --help` and `mini --help`.

## Smoke test FIRST (1 task — do this before any full run)

Always validate end-to-end wiring on a single task before spending tokens on the corpus:

```bash
pier run -p deep-swe/tasks/<task-id> --agent mini-swe-agent \
  --model minimax/minimax-m3 --model-class openrouter
# list available task ids:
ls deep-swe/tasks
```

Pass criteria: run completes, model returns actions (not auth/format errors), a score/trajectory is emitted. If it 401s → key wrong. If "provider not provided"/"model not mapped" → fix slug or switch route.

## Subset run (deterministic sample)

```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model minimax/minimax-m3 --model-class openrouter \
  --n-tasks 10 --sample-seed 0
```

## Full 113-task corpus (costs tokens + time — confirm with user first)

```bash
pier run -p deep-swe/tasks --agent mini-swe-agent \
  --model minimax/minimax-m3 --model-class openrouter
# add `--env modal` to run in parallel Modal sandboxes (needs Modal configured)
```

## Output & leaderboard

- Trials land in `jobs/<run>/<trial_id>/`. Inspect with `pier view jobs/<run>`, `pier analyze jobs/<run>`, or `pier critique run jobs/<run>`.
- Report: the exact command used, pass/fail, score, and any blockers.
- Submit results for the official leaderboard to: **<email-address>**

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| HTTP 401 | bad/missing key | re-export `OPENROUTER_API_KEY` |
| "LLM Provider NOT provided" | missing slug prefix | use Route B `openrouter/...` or Route A with `--model-class openrouter` |
| "model isn't mapped"/cost error | unknown cost for model | `export MSWEA_COST_TRACKING=ignore_errors` |
| unknown flag | version drift | check `pier run --help` |
