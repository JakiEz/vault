---
type: paper-note
description: OptiSAR-Net++ (arXiv 2603.24876) and its OptSAR-RSVG dataset — architecture, how input works (one image, not co-registered pairs), repo facts, and 18 limitations with paper references. Candidate base model for the thesis.
created: 2026-11-11
updated: 2026-11-11
---

# OptiSAR-Net++ / OptSAR-RSVG

Part of [[sar-thesis-hub]]. Source #6 for [[thai-sar-refexp-related-work]]. Modified in [[encoder-swap-experiment-plan]].

**Citation:** Tang, Dong, Cheng, Fan. *OptiSAR-Net++: A Large-Scale Benchmark and Transformer-Free Framework for Cross-Domain Remote Sensing Visual Grounding.* arXiv 2603.24876, Mar 2026. Code: `github.com/JunDong-dev/OptiSAR-Net-PlusPlus`.

## TL;DR

- **Task (CD-RSVG):** one model grounds text queries in **either** optical **or** SAR images.
- **Input = one image + one expression → one box.** It does **not** take co-registered optical+SAR pairs; the paper explicitly rejects that setup (§I: pair-based methods "rely on strictly co-registered image pairs, precluding direct extension to language grounding").
- **Key number:** SAR Pr@0.9 = **37.22%** vs optical **68.89%**. TACMT gets 38.29% on SAR, so the gap is in the data, not this one model.
- **Code is an Ultralytics YOLO fork** with a pluggable text encoder — a good base for Thai experiments.

## Architecture (forward pass)

| Stage | What | Notes |
|---|---|---|
| Input | 1 image (640×640) + 1 query | Tensor `B×C×H×W`; optical and SAR samples share a batch, never a slot |
| Backbone | Shared CSP CNN (YOLOv11 blocks) | Trained from scratch |
| DAA → PL-MoE | 8 LoRA experts, top-2, routed per 2×2 patch | Routes from image content; no domain label in the router |
| TGDF-SSA | Injects text into the feature pyramid | Replaces cross-attention |
| Heads | Box regression + CLIP contrastive matching + auxiliary 4×4 region grid | At inference, one query embedding; highest-scoring region wins (§III-C) |
| Text encoder | MobileCLIP2-B, frozen, 63.4M params | **English only**, which is the blocker for Thai |

Cross-domain sharing happens **in the weights** (`E_e(P) = C_shared(P) + α·P·A_e·B_e`), not in the input. §III-B argues full sharing *hurts* ("feature interference", "SAR-specific cues tend to conflict with optical texture semantics"), so PL-MoE is a **decoupling** module.

Ablations: image-level routing (81.37 meanIoU) loses to patch-level (82.76). The useful shared signal is local structure, not modality.

## Dataset — OptSAR-RSVG

| | Optical | SAR |
|---|---|---|
| Images | 34,359 | 12,466 |
| Instances | 69,970 (77.6%) | 20,178 (22.4%) |
| Categories | 14 | 2 (ships, transmission towers) |
| Sources | RSVGD/RSSVG, OPT-RSVG | SARVG (VGRSS), SARVG1.0 (TACMT) |

Total 46,825 images / 90,148 triplets; 9,046 images / 19,136 annotations come from augmentation plus GPT-4o rewriting. Average expression length is 11.13 words.

## Repo facts (inspected 2026-11-11)

- `ultralytics/nn/text_model.py` — abstract `TextModel` with `tokenize()` + `encode_text()`; factory `build_text_model("base:size")`.
- `scripts/prepare_text_embeddings.py` — text embeddings are **precomputed offline**, so swapping the encoder means regenerating the cache.
- `configs/optisar-net-plusplus-66m.yaml` — head is `OptiSARNetPlusPlusDetect(nc, embed=512, ...)`, so the **text dim must be 512**.
- `ultralytics/data/augment.py` `_ADV_REPLACEMENTS` — hard negatives come from an **English substring table** (`"upper left"`→`"upper right"`, …).

## Limitations (with references)

### Admitted by the authors (§VI)

1. Only optical + SAR; infrared/multispectral unexplored.
2. The CLIP contrastive approach "may face scalability bottlenecks on larger **datasets**" — this is about data size, not parameter count. Untested hedge. See [[sar-imaging-concepts#CNN vs Transformer — long-range dependency]].
3. No temporal modelling. "Image sequences" means **repeat-pass satellite scenes** for change detection, not video. See [[sar-imaging-concepts#Why SAR has no frame rate]].

### Visible in their numbers

4. Loses to TACMT on SAR Pr@0.9 (38.29 vs 37.22) — §V-B.
5. ~31-point optical/SAR gap at Pr@0.9 is never analysed; the paper offers "distribution shifts and imbalanced training data" without evidence — §V-B.
6. PL-MoE, the headline module, adds only +0.75% meanIoU — §V-C.
7. **Modality leaks into the text:** categories carry "Optical"/"SAR" prefixes (§IV-A Step 1) and negatives swap those words (§III-C). Real queries would not say this.
8. Imbalance: SAR is 2 categories and 22.4% of instances — §IV-B.
9. Ablations are reported only on the combined set, with no per-domain ablation — §V-C.
10. Not really "light": the frozen text encoder is 66% of the 95.6M params (§V-A-3).

### Dataset construction

11. **Augment → merge → verify → random 8:1:1 split**, so flipped near-duplicates can sit in both train and test — §IV-A Steps 2–3. *Inferred from the stated order; not yet checked on the released files.*
12. About 21% of annotations are synthetic (augmented images with GPT-rewritten text), and some are in the test set too.
13. 76 fine-grained ship classes were merged into one "ship" class, removing attributes that expressions need — §IV-A Step 1.
14. Manual verification is described in one sentence: no protocol, annotator count, agreement score or removal counts — §IV-A Step 3.
15. The paper's split (37,460/4,682/4,683) differs from the repo's (37,957/4,434/4,434).
16. Only two public SAR grounding sets exist, and both are used, which caps SAR diversity — §IV-A.
17. Expressions are short and single-clause — §IV-B.
18. Failure cases are shown (Fig. 10) but not analysed — §V-D.

**Note for my thesis:** §IV-A Step 1 trains a detector to flag low-IoU annotations for manual review. That is Northcutt-style confident learning applied to boxes, so it weakens the novelty of source #5 in [[thai-sar-refexp-related-work]]. The remaining opening is that their verification is **unspecified and unmeasured** (#14), and it happened before a random split (#11).

## Open checks

- [ ] Run a duplicate-across-split check on the released `train.json` / `test.json` (settles #11 and #15).
- [ ] Ablation: strip the modality prefix (#7).
