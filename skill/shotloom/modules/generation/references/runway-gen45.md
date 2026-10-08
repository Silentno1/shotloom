# Runway Gen-4.5 adapter

Official source: https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5, checked 2026-09-04. Recheck the active interface.

The verified reference snapshot used by this skill records 2–10 second output. For text-to-video, describe both visible world and motion. For image-to-video, the image owns the start; prompt motion and state change rather than repainting it.

Director-owned planning (not a proprietary Runway parameter list) preserves the material starting composition, subject relation, trigger, path, reveal, focus and intended exit. The exit may settle or continue into a cut; use the shared [shot/camera/time guide](../../director/references/shot-camera-time-design.md) only for those decisions. Timestamps represent real ordered events. After repeated failure, change reference/control method or unit boundary rather than adding adjectives.
