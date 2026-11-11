---
type: related-work
description: Related-work table for the Thai referring-expression SAR ship-detection dataset proposal — 5 core sources, each with its key limitation, and the stated research gap (Thai + SAR + RefExp + verified test set).
created: 2026-11-08
updated: 2026-11-11
---

# Related Work — Thai Referring-Expression Dataset for SAR Ship Detection

> Companion to [[sar-visual-grounding-lit-review]] (the broad 2025–2026 field scan). This note is narrower: the **5 foundational sources** the proposal's related-work section argues against, and the precise limitation of each.

## TL;DR

- **Proposal:** a **Thai-language** referring-expression (RefExp) dataset over **SAR** imagery for **ship** grounding, with a **double-checked (human-verified) test set**.
- **Cross-cutting gap:** sources 1–3 are the RefExp canon but are **English + natural photographs**; source 4 gives SAR ship boxes but **no language**; source 5 motivates test-set verification but is **classification-only and model-dependent**.
- **Novelty claim:** the *combination* — Thai + SAR + referring expressions + a verified test set — is unoccupied.

## The five sources

| # | Source | Why it's cited | Key limitation(s) for this project |
|---|---|---|---|
| 1 | Yu et al., **ECCV 2016** — *Modeling Context in Referring Expressions* (**RefCOCO / RefCOCO+**) | The benchmark RefExp datasets | Natural photos (colour + rich texture) ≠ SAR's grayscale, texture-poor speckle; **English**; crowdsourced two-player game → short appearance/location cues; **RefCOCO+ bans location words**, which may be the wrong constraint for ships; assumes clean ground-truth segmentations exist. |
| 2 | Mao et al., **CVPR 2016** — *Generation and Comprehension of Unambiguous Object Descriptions* (**RefCOCOg**) | Longer, "unambiguous" single-target queries | Same natural-image + English bias; collected **non-interactively** — annotators self-judged unambiguity, so QC is weaker than a two-person check; evaluated over **ground-truth proposals**, not raw detector output. |
| 3 | Kazemzadeh et al., **EMNLP 2014** — *ReferItGame* | Source of the **QC method** we adopt (two-person referrer/guesser check) | Oldest and smallest; the game **rewards speed**, which pushes annotators toward terse and ambiguous expressions; never validated on an **expert/sensor domain** or a **non-English** language. We borrow the *protocol*, not the data. |
| 4 | Zhang et al., **Remote Sensing 2021, 13(18):3690** — *SAR Ship Detection Dataset (SSDD): Official Release and Comprehensive Data Analysis* | SAR ship box conventions + baseline imagery | **Detection-only — no language annotations**; small (~1,160 images / ~2,456 ships) and narrow sensor set; **no fine-grained attributes** (ship type, heading, size class) which is exactly what a referring expression needs to disambiguate; inshore/docked ships are visually fused with harbour clutter. |
| 5 | Northcutt et al., **NeurIPS 2021 (Datasets & Benchmarks)** — *Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks* | Evidence that test-set label errors change benchmark rankings → justifies the double-checked test set | Confident learning is **classification-focused** — not boxes, not free-text referring expressions; needs **existing model predictions**, a chicken-and-egg problem for a brand-new dataset; flags *likely* errors but does not define correctness where SAR targets are genuinely ambiguous; supplies **no human re-verification protocol** (so #3 is still needed). |

## How the related-work paragraph should read

1. RefExp grounding is well established — but **only** for English over natural imagery (1, 2), with QC protocols from (3).
2. SAR ship detection is well established — but **purely visual** (4); no referring language, no disambiguating attributes.
3. Test-set label quality is a measured, ranking-changing problem (5) — but the published tooling does not cover boxes or free text, and offers no human protocol.
4. ⇒ No source covers **Thai**, and no source covers **SAR referring expressions with a verified test set**. That intersection is the contribution.

## Open decisions

| Decision | Options | Note |
|---|---|---|
| Allow absolute-location words? | Follow RefCOCO+ (ban) vs. allow | Ships at sea are often *only* disambiguable by position → leaning **allow**, and report it as a deliberate divergence from RefCOCO+. |
| Test-set verification protocol | Adapt ReferItGame two-person check | Needs a concrete spec: referrer writes → independent guesser clicks → disagreement = re-annotate or discard. Not yet written. |
| Attribute vocabulary (Thai) | Type / heading / size / berth state | SSDD gives none of these; must be annotated from scratch. |

## Links

- [[sar-thesis-hub]] — hub for the whole SAR thesis topic.
- [[optisar-net-plusplus]] — **source #6**: the current SOTA cross-domain model/dataset, with 18 limitations. Its label-error filter (§IV-A) weakens the novelty of source #5 above.
- [[thesis-purpose-framing]] — how this gap becomes the thesis statement.
- [[sar-visual-grounding-lit-review]] — broader 2025–2026 SAR grounding field scan (SARVG, SAAVG, OptSAR-RSVG, SARChat-Bench-2M).
- [[cpe-thesis-advisors]] — KMUTT CPE advisor fields, for picking a supervisor for this topic.

---

**Verification status (2026-11-08):** limitations are analytical, derived from the 5 papers' own stated scope and method. Venue/year/ID strings were written from memory and prior-session notes — **check each against the publisher page before submitting**, especially the SSDD counts (1,160 / 2,456) and the Northcutt track name. Full PDFs were not re-opened in this session.
