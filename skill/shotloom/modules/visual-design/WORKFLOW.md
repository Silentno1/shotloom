> Shotloom module, not a separately installed skill. The package [entry](../../SKILL.md) and [environment contract](../../references/environment.md) govern permissions, tool availability and storage. Formal methods may be named references or user-authored; see the shared method-selection contract.

Script checks below are optional tool-assisted forms of the same decisions. Without Python or required media tools, use the documented manual checks and mark unavailable evidence; do not invent a machine pass or block unrelated planning.

# AI Drama Visual Design

Keep three decisions separate:

1. **Production method:** how the images are made or simulated.
2. **Final visual appearance:** what the audience sees.
3. **Platform upload category:** a platform-specific label selected only from its current interface.

They may correlate but are never interchangeable.

## Scope and reading

- Answer a bounded comparison or revise a named design dimension without creating a full visual bible. Reuse approved choices; explain unknowns rather than asking again for decisions already supplied.
- Read the complete work only to establish or materially change the whole-work visual bible. Local work needs the relevant scene/asset, current visual locks and dependencies, not all story files.
- References and validation below are conditional. A valid unchanged contract can be reused; after changes, validate the resulting contract once. Do not run schema checks for a concept explanation with no contract artifact.
- Proposals do not approve assets or overwrite a locked look. Changes to approved locks and file writes follow the user's authorization; task handoffs use the user-selected location, or remain in the conversation when no location is authorized.

## Workflow (select relevant steps)

1. Read the story scope needed above and the relevant approved director method; identify visual obligations and forbidden drift. Formal design requires the current authorized director selection and `director_style_ref`, following [director-selection.md](../director/references/director-selection.md). Run the shared `../director/scripts/director_style.py check PACKET --stage visual` for new/changed formal handoffs. The visual-contract validator alone is not this production gate. Explicit selection exploration can precede the lock but cannot approve formal assets. Do not derive appearance_family from a director's name or copy the reference work's look.
2. When choosing or changing production method or appearance family, use [references/production-method-and-appearance.md](references/production-method-and-appearance.md) and [references/appearance-family-routing.md](references/appearance-family-routing.md). Do not force a universal three-class ontology or a default house style.
3. Read [references/three-render-two.md](references/three-render-two.md) completely only for a chosen/approved whole-work or local mixed-media three-render-two contract, or targeted review of that medium. Follow the shared activation scope in [appearance-family-routing.md](references/appearance-family-routing.md); never relabel a whole mixed work to activate one layer.
4. For asset or spatial design, use [references/asset-and-spatial-systems.md](references/asset-and-spatial-systems.md).
   When learning a look from references, read [references/reference-look-extraction.md](references/reference-look-extraction.md). Separate observed appearance from inferred technique and chosen design; a tutorial's recipe is not a universal requirement. For grids and derived single-shot images, follow the asset guide's derivative workflow.
   For giant subjects, monumental spaces or a shot where relative size is a material design problem, use [references/scale-and-mass.md](references/scale-and-mass.md). It is optional scale design across appearance families, not a default 3D/PBR look or a requirement to add scenery.
5. When a visual bible is requested or its established choices change, use [references/visual-bible.md](references/visual-bible.md); otherwise return only the requested proposal or delta.
   For scene/sequence light, color development or story-bearing environment/prop design, use [references/light-color-production-design.md](references/light-color-production-design.md), retaining the director's intent and chosen medium.
6. Before handing a new or changed visual contract downstream, validate explicit choices with `scripts/visual_contract.py`. The script checks completeness; it does not auto-recommend a look or approve a creative choice.

## Rules

- Never infer animation mechanics from a single attractive still.
- “Anime,” “animation,” “cinematic” and “cyberpunk” are not sufficient visual contracts.
- Those broad words never auto-select three-render-two or any other appearance family.
- Cyberpunk is a story/world-system category, not a rendering method. Neon rain and implants alone do not establish it.
- Mixed 2D/3D techniques do not make the final audience category objectively “2D” or “3D”; describe the visible result and let the actual distribution platform's current choices govern upload classification.
- Asset discovery does not equal approval. Assets have explicit authority levels and intended roles.
- A full character collage never overrides a focused face, body or wardrobe authority. Voice authority is owned by the director/sound contract and approved as an audio asset by review.
- Do not copy a named production's proprietary style. Extract functional constraints.
- Validate common fields for every look and family-specific fields only for the selected appearance family. Never make three-render-two dimensions global requirements.
