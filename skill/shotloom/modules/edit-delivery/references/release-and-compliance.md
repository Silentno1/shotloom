# Creative packaging and platform compliance

## Early use and destination check

During preparation, verify only constraints that materially affect method: intended display/aspect variants, readability and text/subtitle time, required clean/stem/accessibility versions, content disclosures, and provenance/usage permission for voice, music, footage and reference assets. Record the named destination/use and evidence or unresolved dependency; do not invent current legal/platform rules or treat possession of a file as clearance.

Feed consequential findings to composition, generation, sound and post planning before dependent work. Unknown destination does not justify imposing one platform's limits everywhere. Temporary/previs material is not automatically cleared for release. Reverify changing requirements for actual delivery; a prior preparation check is a dated baseline, not permanent approval.

## Creative packaging

Cover, title and description come from the actual released work. Do not invent events, characters or promises. A series cover represents the central relationship rather than one convenient episode frame. Different aspect ratios require independent composition when cropping breaks hierarchy.

## Platform compliance

Inspect the actual current upload interface or first-party rules. Record:

```text
platform and surface
verification date and source
upload category options actually displayed
selected category and rationale based on final appearance
aspect ratio/resolution/frame rate/container/codec/audio
duration and file-size limits
caption/text requirements
cover requirements
content disclosure or moderation fields
QC result
```

For a formal delivery manifest, `qc_result` is structured and its status is `pass` or an explicitly documented `accepted_exception`; a non-empty string such as `failed` is not a pass. Verify that the master exists, its recorded SHA-256 matches, technical metadata is present, and any selected upload category is one of the options actually observed. Use `scripts/delivery_check.py` for these deterministic gates; it still cannot judge creative quality or whether the platform source was interpreted correctly.

Every `accepted_exception` subcheck has a unique name and a matching `qc_result.exceptions` entry with `check`, `reason`, `scope` and `acceptance_source`. The last field identifies explicit, version/range-specific acceptance evidence, not a guess that the user will agree. An exception subcheck requires an `accepted_exception` summary; neither an empty explanation nor a top-level pass can conceal it. Normal passing checks need no exception entries. These fields verify the structure of the evidence, not its truth; inspect the cited acceptance before delivery.

Technical duration must be positive and finite, width/height positive integers, and frame rate a positive finite number or rational string such as `30000/1001`. These are basic validity checks, not a platform specification. Compare supplied metadata to an actual probe of the hash-matched master and its streams; the manifest checker explicitly lists that comparison and source authenticity as not checked. A silent master can record an explicit no-audio state rather than inventing an audio track. Independently verified production method and upload-category labels may be identical; observed options and source evidence govern category selection.

Production method and final visual appearance are evidence for the category choice; they are not the category itself. A three-render-two pipeline may be presented under different labels on different platforms. Never infer a Red Fruit/Hongguo category from a generic animation taxonomy; inspect its current interface.
