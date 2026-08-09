# Generate Image — DeepAPI Endpoint Reference

Generated endpoint reference for the `generate-image` rows of the `deepapi` skill router. Bundle version: ee61bded3e6a. This file is always managed — it is refreshed with the bundle even when `../SKILL.md` has been customized.

Shared protocol (environment, auth, idempotency, dry-run, polling, and error handling) lives in `../SKILL.md`. This file carries the full per-endpoint detail.

## Workflow Guidance

Use this reference to turn a visual brief into a generated image.

### Recommended workflow

1. Capture the subject, purpose, style, composition, aspect ratio, and must-avoid details.
2. When quality matters, generate 2-4 prompt variants and let the user pick; one version is enough only for quick drafts.
3. Match the model to the stakes: the default model is the fast draft tier; use nano-banana-pro or gpt-images-2 for final, customer-facing assets.
4. Save each data URL with an extension matching its MIME type (`image/jpeg` -> `.jpg`, `image/png` -> `.png`); never assume `.png`.
5. After resizing or converting, verify the file decodes and its extension still matches the actual format; treat image-tool warnings as failures.
6. If published, verify the image renders on the live page before reporting success.
7. Return the resulting asset and summarize the prompt choices.
8. Iterate only on concrete feedback; preserve constraints that were not changed.

## Endpoint Details

## Generate Image

`POST /v1/generate/image`

Generate an image from a text prompt.

- Capability: `generate.image`
- Scope: `generate:image`
- Side effects: Runs a paid image generation request and debits credits when finished.
- Cost: The default cap follows the model: maxCostUsd 0.375 for nano-banana-2 (the default) and seedream-4.5, 1.50 for nano-banana-pro and gpt-images-2. Pass maxCostUsd or maxCostMicrousd to choose a different customer spend cap. The final debit is capped and reported as debitMicrousd. Typical price: ~$0.20-$1.13 per image depending on the model.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- Describe the image you want in prompt, including style and composition.
- Omit model for the default; pick one only when you need its specific strength (premium models cost more per image).
- output.images contains base64 data URLs; save them to files instead of printing them.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "prompt"
  ],
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Text description of the image to generate."
    },
    "model": {
      "type": "string",
      "enum": [
        "nano-banana-2",
        "nano-banana-pro",
        "gpt-images-2",
        "seedream-4.5"
      ],
      "default": "nano-banana-2",
      "description": "Optional image model. nano-banana-2 (default): fast, balanced quality. nano-banana-pro: highest fidelity for demanding work. gpt-images-2: strongest complex instruction following. seedream-4.5: budget generation and editing-style prompts."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "0.375",
      "description": "Optional customer spend cap in USD. Defaults per model: 0.375 for nano-banana-2 and seedream-4.5, 1.50 for nano-banana-pro and gpt-images-2."
    },
    "maxCostMicrousd": {
      "type": "integer",
      "minimum": 1,
      "description": "Optional customer spend cap in USD micro-dollars."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "prompt": "A minimal flat illustration of a rocket launching from a laptop screen",
  "maxCostUsd": "0.375"
}
```
