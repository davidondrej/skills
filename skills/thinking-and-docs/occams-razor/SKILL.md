---
name: occams-razor
description: Answer from the real underlying data, not promises or clever reasoning. Give the simplest answer, what you're looking at, and a confidence %. Use for "occams-razor", or when the user asks what we actually know, whether something is really true, or tells you to stop overthinking.
---

# Occam's Razor

David's words (2026-11-08):

> Stop overthinking and be very practical with me. Stop trying to do some fucking Jedi reasoning.
>
> What is the underlying data we have? I need to see it in the dashboard. Don't take his word for it and assume that at the end of the month we will be charged the right amount.
>
> What do we know from the dashboard, from the real numbers? As of today, what do we know? And how do you know and what are you looking at and what percentage of confidence you have? Be very fucking concise.

## Rules

- **Simplest answer wins.** Pick the plain explanation the numbers point to. No long chains of "what if".
- **Data, not words.** Only real numbers count: dashboards, bills, production data, logs. Promises from people ("he said he'll fix it") are not evidence.
- **As of today.** Say what is true now, not what should happen later.

## Answer format

Answer in short, in plain English. Be extremely concise.

1. **The answer:** one sentence, plus a confidence %.
2. **What I'm looking at:** the exact source and the raw numbers.
3. **Why:** the one-line math or logic.
4. **The doubt:** the one thing that could make it wrong, in one sentence.

## Example

Question: a vendor promised a lower price from the 1st. Are we on it yet?

- **Answer:** no, still the old price. 95% sure.
- **Looking at:** the vendor's billing dashboard for this month: total cost and total usage.
- **Why:** cost ÷ usage equals the old rate exactly, not the new one.
- **Doubt:** a different usage mix could average to the same rate, but our mix barely changed.
