---
name: risky-changes
description: 'Verify assumptions before implementing large or risky changes to APIs, provider data, billing, pricing, quotas, or defaults. Use when a mistake could affect customers or the user asks if a change is safe to ship. Checks real-world impact beyond passing tests.'
---

# Risky Changes

A filter once passed every test but disabled ~99% of the feature on live data. Tests check code correctness; research and live measurement check whether a change is useful.

## When this applies

Use for changes where being wrong is expensive or customer-visible:

- Public API fields, filters, or response shaping
- Dropping, transforming, or reordering upstream data
- Billing, pricing, caps, or quotas
- Defaults, thresholds, or provider request parameters
- Unverified assumptions about external data or user behavior

If unsure whether a change qualifies, apply this process.

## 1. Identify assumptions

List the assumptions the change depends on. Mark which have evidence and which are still unverified.

## 2. Research before implementing

Use available research tools and reliable sources. Investigate each distinct question separately, covering at least:

- How do leading products handle this design decision?
- What does real-world data look like: frequencies, shapes, and edge cases?
- What do users or agents actually need?

If evidence contradicts an assumption, reconsider the design before coding. If research is unavailable or inconclusive, state the gap; do not treat the assumption as verified. Do not ship while material assumptions remain unverified.

## 3. Measure real behavior

Run 10–20+ realistic cases against the real endpoint or provider:

- Base cases on real usage; vary topics, parameters, languages, and edge conditions.
- Define benchmarks per case: speed, quality, accuracy, and how often the new behavior occurs.
- Use hard numbers where possible. For subjective quality, use blind, criteria-based judging.
- Compare before and after when both can be measured.
- Read-only production analysis also counts as measurement.

Save the cases and results in the project's evals folder, e.g. `docs/evals/YYYY-MM-DD-<endpoint>-<focus>.md`. Create the folder if needed. Without this record, the change is not verified. Unit tests do not replace live measurement.

## 4. Confirm product-owner approval before shipping

Present decisions that affect what customers see or pay, with supporting research and measurements. Get the product owner's approval for those decisions; do not bury them in a plan or code default. Existing approval counts if it covers the actual behavior being shipped.

## 5. Verify after deployment

Within one day, measure the change on real traffic through read-only production analysis or a live sweep. Report results that differ from expectations immediately.
