# Paper synchronization audit — 2026-08-01

## Completed

- synchronized the manuscript with the unversioned `release/`, `audit/`, and `evaluation/` directories;
- preserved 328/328 source replay evidence, executed all 328 serialized release-call sequences, and independently executed all 147 AppWorld official solutions;
- removed external-model judging, privacy-probe claims, and model-generated review translations from the delivery boundary;
- retained the 80-item blinded source-text review workflow without treating empty templates as human labels, and changed presentation to a label-independent global permutation;
- explicitly retained `minimality_verified=false` and avoided claiming a globally minimal reference path.
- documented the AppWorld protected-data encryption condition and separated the data-free Python distribution from private research artifacts.
- renamed the over-broad persistent `private_notes` field to task-scoped `private_text`, then regenerated the release, audit, review, Web, and paper evidence from locked sources.

## Evidence boundary

The manuscript distinguishes source replay, serialized release-call execution, AppWorld official-solution execution, and final-state verification. Formal conversion and release checks use deterministic source evidence rather than an external semantic judge. Human agreement still requires two independent reviewers.

## PDF regeneration status

- The manuscript sources and machine-readable evidence now describe the 328-case release.
- The synchronized manuscript compiles successfully with XeLaTeX/BibTeX to a 17-page A4 PDF.
- Final PDF SHA-256: `ecfa63828c11a9f4d356c0ec1e69e3a62925538d5c9f5b90284d2577be345c8c`.
- Text extraction contains the current 328-case/API-Bank Level-1/2 metrics and no stale 324-case or Level-3 claims.
- All 17 rendered pages passed the visual gate: no clipping, overlap, missing glyphs, unresolved references, or broken figures/tables were observed.
