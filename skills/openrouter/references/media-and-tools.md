# Images, other media, and tools

## Image generation and aspect ratios

- As of 2026-09-09, `openai/gpt-image-2.5-sunburst` is OpenAI's latest and best model for image creation and editing when quality is the priority. Prefer it for polished YouTube thumbnails and precise edits; Flare prioritizes speed. [OpenAI comparison](https://openai.com/index/introducing-chatgpt-images-2-5/#images-25-in-the-api), [OpenRouter model](https://openrouter.ai/openai/gpt-image-2.5-sunburst). Recheck live availability and capabilities before use.
- `openai/gpt-image-2.5-flare` is the faster OpenRouter API alternative to `openai/gpt-image-2.5-sunburst` for image creation and editing. Prefer Flare for quick iterations; prefer Sunburst when quality and precise editing matter most. [OpenRouter model](https://openrouter.ai/openai/gpt-image-2.5-flare), [OpenAI comparison](https://openai.com/index/introducing-chatgpt-images-2-5/#images-25-in-the-api).
- Check the image model's `/api/v1/images/models/{author}/{slug}/endpoints` record for `supported_parameters.aspect_ratio.values`. The general API ratio list is not a promise that every model supports every ratio.
- Verified 2026-09-07: `openai/gpt-5.4-image-2` lists `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, plus `auto`. Recheck the [live model settings](https://openrouter.ai/api/v1/images/models/openai/gpt-5.4-image-2/endpoints) before use.
- `5:2` is not listed; `21:9` is the closest listed ratio. Do not assume custom pixel dimensions bypass the model's limits.
- In Chat Completions, use `"modalities": ["image", "text"]` and `"image_config": {"aspect_ratio": "21:9"}`. The dedicated Image API (`POST /api/v1/images`) uses top-level `"aspect_ratio": "21:9"`. A prompt suffix such as `--ar 5:2` is not an OpenRouter API setting. [Chat schema](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion#body-image-config), [Image API docs](https://openrouter.ai/docs/guides/overview/multimodal/image-generation#resolution-and-aspect-ratio).

## Image attachments in Chat Completions

Use a `content` array, with text first and one part per image. A URL must be accessible to the service. For local/private files use a complete data URL with the correct MIME type, rather than publishing a private attachment just to obtain a URL.

```json
{
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "Compare these two images."},
      {"type": "image_url", "image_url": {"url": "https://example.com/first.png", "detail": "auto"}},
      {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,BASE64_BYTES", "detail": "auto"}}
    ]
  }]
}
```

This is a body fragment with placeholder content. Add the verified model/fallback, reasoning, limits, and provider settings from the main workflow. Every possible model must support image input and the requested number/size of images.

PNG, JPEG, WebP, and GIF are documented. Limits vary by endpoint. `detail` supports `auto`, `low`, `high`, and the OpenRouter `original` extension; the latter can be downgraded to high. Lower detail may reduce cost but lose small text. Resize only when the task still works. Do not log data URLs or signed URLs. If your app fetches user URLs itself, validate destinations and redirect behavior. [Image inputs](https://openrouter.ai/docs/guides/overview/multimodal/image-understanding), [content schema](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion)

## PDF, audio, and video inputs

Use the correct content-part shape; these are not interchangeable:

```json
{"type": "file", "file": {"filename": "document.pdf", "file_data": "data:application/pdf;base64,BASE64_BYTES"}}
```

PDF parsing may use native support or a file-parser plugin. The documented default can fall back to paid OCR. Verify engine, price, privacy, and image handling before uploading documents. Native PDF support and OCR-to-text are not equivalent for charts. Reuse returned file annotations where documented to avoid repeat parsing, but store them privately. [PDF inputs](https://openrouter.ai/docs/guides/overview/multimodal/pdfs)

```json
{"type": "input_audio", "input_audio": {"data": "RAW_BASE64_BYTES", "format": "wav"}}
```

Audio input uses raw base64 plus a format, not an image-style data URL or a direct hosted URL. Supported formats depend on the model. Audio output through Chat requires its documented `audio` configuration, compatible output modalities, and streaming. Dedicated speech/transcription APIs have different request contracts. [Audio](https://openrouter.ai/docs/guides/overview/multimodal/audio)

```json
{"type": "video_url", "video_url": {"url": "https://example.com/clip.mp4"}}
```

Use `video_url`; the old `input_video` discriminator is deprecated. Check input-video support, size/duration restrictions, and transport for the selected endpoint. Video generation is a **separate asynchronous API**: create, poll the returned job URL, then download. Do not treat its first 202 response as a finished video or invent Chat-compatible fields. Inspect its dedicated model capabilities and privacy restrictions. [Chat video schema](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion), [video generation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)

## Tool calls

Declare client tools as `tools: [{"type": "function", "function": {"name": "...", "description": "...", "parameters": SCHEMA}}]`. Use schema strictness only where supported. `tool_choice` can be `auto`, `none`, `required`, or a named function. `parallel_tool_calls: false` requests serial calling. [Tool contract](https://openrouter.ai/docs/guides/features/tool-calling)

The application owns execution:

1. Read `tool_calls`; null assistant text is valid at this point.
2. Validate the function name and arguments against the allowed tool schema. Apply the application's authorization policy before side effects.
3. Preserve the assistant message and its tool calls. Append one tool result with the matching `tool_call_id` for each executed call.
4. Send the conversation and tool definitions again, preserving the selected reasoning configuration. Bound iterations and total spending.

```json
{
  "role": "tool",
  "tool_call_id": "ID_FROM_ASSISTANT_TOOL_CALL",
  "content": "{\"result\":\"tool output\"}"
}
```

When reasoning models return `reasoning_details`, preserve required blocks and their order **unchanged** for continuation, including opaque/encrypted data and signatures. Do not invent reasoning or substitute it for the final answer. Keep this state separate from logs. Verify compatibility before switching models mid-tool-loop; an opaque provider-specific block is not necessarily portable. [Reasoning preservation](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens#preserving-reasoning-blocks)

For streaming, assemble tool calls by choice and tool indexes, append argument fragments, then parse complete JSON. Do not execute partial fragments or treat repeated terminal/usage frames as another tool call. Provider-run server tools/plugins have different execution and billing contracts; do not apply client-tool assumptions to them.
