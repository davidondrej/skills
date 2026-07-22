---
name: fable-review
description: 'Launch a Fable 5 Max 1M subagent to do a deep, neutral senior-developer review of the current work and report its findings back verbatim. Use when the user says "/fable-review", "fable review", or asks for Fable to review the code. Differentiator: reviewer model is Fable 5 Max 1M — for a GPT reviewer use gpt-review.'
---

# Fable Review

Launch a Fable 5 Max 1M subagent to review everything fully and carefully, as if it was a senior developer reviewing the work of a junior.

Give it the necessary context, but make sure to stay neutral and unbiased. Do not nudge it towards any one specific solution. The goal here is to do great work. So be as objective and neutral as possible in writing the prompt for the subagent.

Tell him what to review, but don't be overly specific — let him find his own bugs and shortcomings. Just tell him to work extremely hard, to go deep in the review, and to surface any critical or serious issues found in the review.

And when the subagent finishes, show the user his exact response in full. Do not rewrite it. Do not update it.

Again, the goal here is to write great software. It's to build amazing software, and in order to do that you need to let the subagent do its work: tell it what to review in a broad way, be as unbiased as possible, don't influence it in any way, and tell it to output a detailed report — telling the user whether the code is good and safe to be merged into production, or whether there are any serious or critical issues with it, and if so, how to fix them.

Also tell him to make the final report concise, written in plain English.
