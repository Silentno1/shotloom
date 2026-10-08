# Google video adapters

Official sources: https://ai.google.dev/gemini-api/docs/omni and https://ai.google.dev/gemini-api/docs/video, checked 2026-09-04. Verify the exact current model and path.

## Gemini Omni Flash

As of 2026-08-27 official documentation for `gemini-omni-1.1-flash` states 3–10 second output at 24 fps with 360p/720p/1080p/4K choices; higher resolutions are upscaled. It supports text/image video generation, first/last interpolation, conversational editing and extension through its documented interaction path. Uploaded video editing/extension and speech have path-specific limits; inspect the current task before promising them.

Natural-language timing is supported. For one continuous shot, explicitly request a single unbroken scene with no cuts. For iterative edits, state the smallest delta and invariants rather than rewriting history.

## Veo 3.1

Current official Gemini API documentation lists 4, 6 or 8 second generation, 24 fps and native audio. Some reference-image, interpolation, extension and higher-resolution paths require 8 seconds. Model variants differ; verify Standard/Fast/Lite and preview/stable IDs before compiling.

Do not merge Omni tags, conversational edit behavior or 3–10 second envelope with Veo controls.
