---
name: image-prompt
description: 'Write four distinct prompts for AI image models. Use for image, thumbnail, banner, logo, or illustration prompts. Produces prompt text only.'
---

# Image Prompt

Write 4 model-agnostic prompt variations that the user can paste into any image model.

## Output format

- Exactly 4 variations, each one paragraph in its own fenced code block. Nothing else inside.
- Always use a `text` fence so it renders as a full copyable block, not a tiny snippet. Pattern:
  1. Blank line after the label
  2. Opening fence on its own line: three backticks then `text`
  3. The prompt paragraph
  4. Closing fence on its own line
- Never wrap a prompt in single backticks. Never use a bare unlabeled fence. Those render as small snippets and are hard to copy.
- Every prompt ends with ` --ar 1:1`. It is the Midjourney aspect-ratio flag and is harmless in other models. If the user names an aspect ratio, use that instead (e.g. `--ar 16:9`).
- A 3-5 word label above each block is fine. No commentary, no explanations, no questions after.

## How to write each prompt

Describe a finished piece in clear, expressive, descriptive prose. Each paragraph covers:

1. **Subject** — what it is, what it is doing, the defining details.
2. **Environment** — where it sits, background, lighting, time of day.
3. **Color palette** — name the dominant colors and the contrast.
4. **Vibe and feeling** — the mood and the emotion the image should evoke.
5. **Style / medium** — photograph, cinematic still, 3D render, oil painting, flat vector, etc.

## Rules

- Descriptive prose only. No bullet lists inside a prompt, no "imagine a...", no "create an image of".
- Make the 4 variations genuinely different — different style, composition, mood, or palette. Not rewordings of one idea.
- No text inside the image unless the user asks; models render text badly.
- No negative prompts and no model-specific parameters other than `--ar`.
- If the request is vague, still deliver 4 prompts. Pick sensible defaults, do not ask questions.

## Example

Request: "logo concept for Vectal Labs, something about invention"

**Filament in the void**

```text
A single glowing filament bulb suspended in a vast dark void, its wire coiled into a rising spiral, casting warm amber light onto faint blueprint lines etched into black glass beneath it. Deep charcoal and midnight blue with one accent of molten gold. Quiet and reverent, the feeling of a first idea arriving at 3 a.m. Minimal, high contrast, rendered like a luxury product photograph. --ar 1:1
```

(…then three more, each in its own code block, each a different direction.)
