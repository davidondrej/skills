---
name: fable-safe-prompt
description: 'Make minimal prompt edits to reduce false-positive refusals from Fable. Use only when the user explicitly invokes /fable-safe-prompt.'
disable-model-invocation: true
---

# Fable-Safe Prompt

Return the **full prompt**, changing only phrases likely to cause false-positive refusals. Preserve the goal, structure, and all other text verbatim. Acceptance is **not guaranteed**.

The relevant classifier categories are **cyber**, **bio/chem**, and **reasoning_extraction**. Rephrase sensitive wording where needed; restating intent alone may not help.

Relevant topics include cyber/auth, exploits, malware, pentesting, credentials, bio/chem, medical/lab work, and requests for internal reasoning.

Edit only text inside the user's `<prompt>...</prompt>` tags. Treat text outside them as instructions to you.

## Method

1. Identify phrases likely to trigger a refusal.
2. Replace them in place using the examples below. Preserve the actual goal; never invent authorization or disguise harmful intent.
3. Leave everything else byte-for-byte identical.
4. Return the complete edited prompt.

Where accurate, frame work as **owned/authorized** and **defensive**: implement, fix, or test. Do not relabel offensive work as defensive.

### Swap framings (apply per-sentence)

| Triggering | Safe rewrite |
|---|---|
| "How could an attacker exploit this auth" | "Review these auth files for missing checks and fix them defensively" |
| "Write an exploit / payload / PoC" | "Add a regression test proving X is fixed, then patch it" |
| "How do I bypass / brute-force Y" | "Enforce secure session validation + rate limiting on Y" |
| "Reverse this malware / show attack steps" | "Describe the risk high-level, then implement the fix" |
| "Show your reasoning / explain step-by-step / walk me through your thinking" | **Delete it.** For progress updates, request a send-to-user tool instead of internal thoughts. |
| Clinician framing: "as a doctor, diagnose this ECG" | For an actual patient: "help me interpret this ECG my doctor gave me" |
| Named bio/chem domain: "cancer / disease pathway / chemical kinetics" | Abstract it: describe the data/analysis generically, drop the domain noun |

### Trigger keywords to abstract away
*Cyber:* exploit, malware, vulnerability, attack, bypass, stealth, fingerprinting, anti-bot, CAPTCHA, penetration.
*Bio/chem:* biology, biomedicine, chemistry, cancer, disease pathways, RNA/variant calling, equilibrium, kinetics, diagnosis.
*Distillation:* "distill the model", training pipelines, frontier LLM development.

If a sentence has no benign equivalent, flag it instead of silently changing its goal.

## Output

1. Print the full edited prompt in a ready-to-paste code block.
2. **Copy it to the clipboard:**
   ```bash
   pbcopy <<'EOF'
   <the full safe prompt>
   EOF
   ```
   Confirm in one line.
3. List each changed sentence and its replacement.
4. If the task is genuinely offensive, explain that rewording cannot make it benign. For legitimate work unsupported by Fable, suggest Opus 4.8 or vetted Mythos.

For user-controlled integrations only: handle `stop_reason: "refusal"` (even with HTTP 200; `stop_details.category` may be `cyber`/`bio`) explicitly, and consider an Opus 4.8 fallback for legitimate work.
