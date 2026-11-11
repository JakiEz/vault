---
type: moc
description: Hub for the 4th-year SAR thesis (Thai referring expressions for SAR ship grounding) — links every note on the topic and shows how they connect. Start here.
created: 2026-11-11
updated: 2026-11-11
---

# SAR Thesis Hub — Thai Referring-Expression SAR Ship Grounding

> Map of Content for the senior project. Open Obsidian **Graph view** (or [[sar-thesis-map.canvas]]) to see the connections visually.

## TL;DR

- **Project:** a small, **human-verified** Thai-language referring-expression benchmark for **SAR ship** grounding, plus experiments adapting an existing model (OptiSAR-Net++) to Thai.
- **Core claim:** SAR grounding collapses at strict IoU (~37% Pr@0.9 vs ~69% optical). Nobody knows whether that is the **model** or the **labels**; a verified test set can tell them apart.
- **Status (2026-11-11):** literature mapped, base model chosen and inspected, experiment plan drafted. Next: pick SAR-only vs joint training, then write the Thai text-encoder subclass.

## How the notes connect

```
                 [[sar-visual-grounding-lit-review]]   (field scan, 2025–2026)
                                │ narrows to
                                ▼
 [[sar-imaging-concepts]] ──► [[thai-sar-refexp-related-work]]   (5 foundational sources)
   (physics background)         │ + source #6
                                ▼
                       [[optisar-net-plusplus]]   (base model + 18 limitations)
                         │                    │
              motivates  ▼                    ▼  is modified by
         [[thesis-purpose-framing]] ◄──── [[encoder-swap-experiment-plan]]
              (why it matters)     tests     (what we change and why)
                         │
                         ▼
                [[cpe-thesis-advisors]]   (who could supervise)
```

## Notes

| Note | Role | Read it when |
|---|---|---|
| [[sar-visual-grounding-lit-review]] | Broad field scan: datasets, SAR VLMs, ranked gaps | You need the landscape |
| [[thai-sar-refexp-related-work]] | The 5 sources the related-work section argues against | Writing the proposal |
| [[optisar-net-plusplus]] | Base model: architecture, input format, 18 limitations | Designing experiments |
| [[thesis-purpose-framing]] | Why the project is useful; 4 framings ranked | Writing motivation / defending |
| [[encoder-swap-experiment-plan]] | What to change in the model and why each change is justified | Running experiments |
| [[sar-imaging-concepts]] | SAR physics: synthetic aperture, revisit, speckle, why ships break pairing | Answering committee questions |
| [[cpe-thesis-advisors]] | KMUTT CPE advisors | Choosing a supervisor |

## Open decisions

| Decision | Options | Where discussed |
|---|---|---|
| Training regime | SAR-only (lean) vs joint optical+SAR | [[encoder-swap-experiment-plan]] |
| Allow absolute-location words? | Ban (RefCOCO+) vs allow | [[thai-sar-refexp-related-work]] |
| Verification protocol | Two-person referrer/guesser check (ReferItGame) | [[thai-sar-refexp-related-work]] |
| Thai operational user | Confirm GISTDA / ศรชล / Dept. of Fisheries use of SAR | [[thesis-purpose-framing]] |

## Log

- **2026-11-08** — Related-work table for the 5 foundational sources written.
- **2026-11-09** — OptiSAR-Net++ read in full: single-image input, rejects co-registered pairs; 18 limitations listed; purpose framings drafted.
- **2026-11-11** — Repo inspected (Ultralytics/YOLO fork, pluggable `TextModel`); experiment plan drafted; this hub created.
