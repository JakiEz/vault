---
type: project-note
description: Why the Thai SAR referring-expression project is useful — four candidate purpose framings ranked by how well they survive a defense, the recommended thesis statement, and scope limits.
created: 2026-11-11
updated: 2026-11-11
---

# Thesis Purpose — Why This Project Matters

Part of [[sar-thesis-hub]]. Evidence comes from [[optisar-net-plusplus]] and [[sar-visual-grounding-lit-review]]; tested by [[encoder-swap-experiment-plan]].

## TL;DR

- **Lead with measurement integrity:** is SAR's strict-IoU failure caused by the model or the labels? A verified test set can tell them apart.
- **Scope claim:** Thai multimodal AI has no remote-sensing or grounding coverage.
- The operational (IUU fishing) and linguistic (no word spaces) arguments are **supporting**, not core.

**Thesis statement (draft):**
> We build a verified Thai SAR ship referring-expression benchmark to determine whether the persistent failure of SAR grounding at strict IoU is a modelling limitation or an annotation artifact.

## Framings ranked

| Rank | Framing | Strength | Evidence | Weak point |
|---|---|---|---|---|
| **C** | Measurement integrity | Strongest | Every SAR method sits around 37–38% Pr@0.9 vs 69% optical ([[optisar-net-plusplus]] #4–5); OptSAR-RSVG split ordering (#11) | OptSAR-RSVG already claims manual verification, so argue *unspecified*, not *absent* |
| **D** | Thai multimodal AI has no RS/grounding coverage | Strong | Typhoon2-Vision, Typhoon OCR and ThaiOCRBench (2,808 samples, 13 tasks) are all document/OCR-focused | — |
| **A** | Thai maritime enforcement (IUU, dark vessels) | Weak as stated | SAR sees through SE-Asian monsoon cloud; xView3-SAR (NeurIPS 2022, 991 Sentinel-1 scenes, analyst-verified) | **No evidence found yet** that a Thai agency uses SAR ship detection |
| **B** | Thai has no word spaces | Weakest | Thai segmentation is a known problem (AttaCut, BEST, LST20) | Subword tokenizers largely work around it |

## What D gives for free

Run **Typhoon2-qwen2vl-7b-vision-instruct** zero-shot on the benchmark. It is Apache-2.0, needs no training, and gives a full results chapter: "the leading Thai VLM scores X on Thai SAR grounding."

## Scope (keep it finishable)

| Decision | Choice |
|---|---|
| Test set | A few hundred human-verified items, two-person check |
| Train set | Machine-translated existing SAR grounding data, **not** hand-annotated |
| Model | Adapt existing ones ([[optisar-net-plusplus]]); no new architecture |
| Temporal / multi-sensor | Future work only (see [[sar-imaging-concepts]]) |

## To verify (in Thai)

- [ ] GISTDA (สำนักงานพัฒนาเทคโนโลยีอวกาศและภูมิสารสนเทศ) — satellite assets, any Sentinel-1 maritime service
- [ ] Thai-MECC (ศรชล) — use of SAR
- [ ] Department of Fisheries — VMS program
- [ ] EU IUU yellow card for Thailand: issued 2015, lifted 2019 (dates from memory — confirm)
