# Research ethics and execution boundaries

**Status: PROVISIONAL, amended 2026-10-08.**

The implemented pilot interprets bounded JSON policies for bin packing. It never executes model-authored Python. The absence of candidate I/O primitives and bounded expression structure is a language restriction, not an OS sandbox claim. Arbitrary program execution requires a separate containment design and escape tests before adoption.

The API client reads only the configured credential/settings names, never sends `.env` as prompt content, and never records keys or raw exception headers/bodies. Task prompts and model replies are retained locally for reproducibility. `.env` and runtime output directories are ignored by Git. Review logs and endpoint metadata before any public release.

The current reference set consists of project-authored implementations of standard named heuristics. The bibliography is not an ingested or licensed full-text corpus. Future corpus ingestion must record each source version, provenance, and permitted uses; public accessibility does not imply unlimited redistribution rights.

Record measured API usage and failures. No measured carbon footprint or provider FLOP count is currently available; do not invent one from token totals. Report any future estimates with their assumptions.

No human participants are recruited in this pilot. Future expert studies need informed consent, appropriate institutional review where applicable, compensation, limited collection of identifying information, and predefined anonymization and retention rules.

Negative results, incomplete runs, and unresolved novelty judgments are retained. Bibliography entries and result claims must be grounded in source evidence. Improvements within a restricted benchmark must not be described as inventions never seen in human history.
