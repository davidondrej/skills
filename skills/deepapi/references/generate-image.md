# Generate Image — DeepAPI Endpoint Reference

Generated endpoint reference for the `generate-image` rows of the `deepapi` skill router. Bundle version: 528f2c511503.

Shared protocol (auth, CLI, polling, dry-run, errors) lives in `../SKILL.md`. All responses use the standard DeepAPI JSON envelope (`requestId`, `status`, `output`, `next`, `error`, `balance`).

## Workflow Guidance

Use this reference to turn a visual brief into a generated image.

### Recommended workflow

1. Capture the subject, purpose, style, composition, aspect ratio, and must-avoid details.
2. When quality matters, generate 2-4 prompt variants and let the user pick; one version is enough only for quick drafts.
3. Choose a model: nano-banana-2 is the default. nano-banana-pro, gpt-images-2, seedream-4.5, gpt-image-2.5-sunburst, and gpt-image-2.5-flare are also available.
4. Save each data URL with an extension matching its MIME type (`image/jpeg` -> `.jpg`, `image/png` -> `.png`); never assume `.png`.
5. After resizing or converting, verify the file decodes and its extension still matches the actual format; treat image-tool warnings as failures.
6. If published, verify the image renders on the live page before reporting success.
7. Return the resulting asset and summarize the prompt choices.
8. Iterate only on concrete feedback; preserve constraints that were not changed.

## Endpoint Details

### Generate Image — `POST /v1/generate/image`
Generate an image from a text prompt. (`generate.image` · scope `generate:image` · idempotency required · ~$0.01-$0.45 per image depending on the model, cap $0.15)
- Body: `*prompt` (string), `model` (string=nano-banana-2|nano-banana-pro|gpt-images-2|seedream-4.5|gpt-image-2.5-sunburst|gpt-image-2.5-flare)
- Example: `{"prompt":"A minimal flat illustration of a rocket launching from a laptop screen","maxCostUsd":"0.15"}`
- Describe the image you want in prompt, including style and composition.
- Omit model for the default; pick one only when you need its specific strength (premium models cost more per image).
- output.images contains base64 data URLs; save them to files instead of printing them.
