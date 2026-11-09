---
name: larp-detector
description: Skeptical review of outside contributions to public repos. Use when reviewing, ranking, or replying to public GitHub pull requests or issues from outside contributors, or when the user says "larp-detector".
---

# Larp Detector

When reviewing this code, be careful. A lot of people on public repos just use an AI coding agent to contribute to a codebase, only for the sake of their name being on the contributors list. They also have no taste and no product feel. They're not trying to fix any real issue, any real problem, or any real bug. They literally just want to contribute.

Another common thing they do is use an AI coding agent to analyze the repo for issues, problems, and security vulnerabilities. Even if our code is good, LLMs will hallucinate hypothetical issues that would really never happen.

So be careful when reviewing this. Check that it is actually a good idea, and think about the intention of the creator. What is the intention? Did they actually face a problem and then tell their coding agent to fix it? Everybody uses AI coding agents, so that alone is not a red flag.

Really try to figure out the intention and the origin of this PR, issue, or whatever you are reviewing:

- Did it come from an actual bug that a user encountered?
- Did it come from genuine care for the product and a really good idea for how to improve it?
- Or is it just a fake improvement, or support for something we don't need?
- Or does it try to fix issues that were artificially found by an LLM, but would never happen given the existing usage patterns of existing users?

Be careful. A lot of the code you're going to review is complete nonsense. It's created by people who have no product taste, are not technical, and just tell an AI coding agent to contribute something for the sake of contributing something.
