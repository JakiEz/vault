---
type: experiment-plan
description: Plan for adapting OptiSAR-Net++ to Thai SAR grounding — encoder candidates, the 4 justified changes, what to keep, and the SAR-only vs joint-training decision.
created: 2026-11-11
updated: 2026-11-11
---

# Experiment Plan — Adapting OptiSAR-Net++ to Thai

Part of [[sar-thesis-hub]]. Base model: [[optisar-net-plusplus]]. Tests the claims in [[thesis-purpose-framing]].

## TL;DR

- **Goal is not to beat them.** Every change must have a reason that holds up on its own.
- Fine-tune from their `best.pt` (they trained 300 epochs on 8× RTX 4090, which is out of reach).
- **Change:** text encoder, Thai hard negatives, drop the modality prefix, report results by object size.
- **Keep:** backbone, fusion, region head, losses.

## Justified changes

| # | Change | Reason | Experiment |
|---|---|---|---|
| 1 | Text encoder → multilingual, image-aligned, kept frozen | MobileCLIP2-B cannot read Thai; head needs `embed=512` | Old vs new encoder on English, then new on Thai — separates encoder cost from language cost |
| 2 | Thai adversarial negatives on segmented words | English substring table never matches Thai, so the mechanism would silently turn off | With vs without |
| 3 | Remove "SAR"/"Optical" prefix and modality-swap negatives | Single-domain data; real operators don't type it ([[optisar-net-plusplus]] #7) | Prefix vs no prefix |
| 4 | Pr@0.9 split by object size | SAR targets are mostly small; 1–2 px error fails IoU 0.9 | Evaluation only, no training |

**Thai negatives caveat:** segment first (PyThaiNLP). "บน" means both "upper" and "on", so blind replacement corrupts non-spatial sentences.

## Hypothesis to test before changing

If #4 shows small objects drive the Pr@0.9 failures → try 1024 input instead of 640 → if that helps, add a stride-4 pyramid level. If it doesn't help, the cause points to labels, which supports framing C in [[thesis-purpose-framing]].

## Text encoder candidates

| Candidate | Dim | Thai | Image-aligned | Use |
|---|---|---|---|---|
| jina-clip-v2 | 1024 (Matryoshka → 512) | Yes | Yes | **Main pick.** CC-BY-NC-4.0 (fine for a thesis) |
| SigLIP 2 multilingual | 768 | Yes | Yes | Second pick; needs 768→512 linear |
| WangchanBERTa | 768 | Native | No | Ablation: Thai-native vs image-aligned |
| XLM-R base | 768 | Yes | No | Control |
| M-CLIP | — | Unverified | Yes | Check first |
| Typhoon2-Vision | — | Yes | Partly | Zero-shot baseline, not a swap |

Not yet verified: Thai quality of jina-clip-v2 after truncation to 512; whether head-only fine-tuning is enough after the text space changes (use the repo's 1%-data dry run).

## Visual encoder (stretch / future work)

| Option | Cost |
|---|---|
| Change `scale:` n/s/m/l/x in the YAML | One line — free capacity ablation |
| SARATR-X (HiViT, self-supervised SAR) | High: ViT gives single-scale tokens; needs a feature-pyramid adapter and PL-MoE re-tuning |
| SARCLIP ViT-L/14 (SAR+text contrastive) | High, and its text side is English |

## Keep as-is

Backbone, TGDF-SSA fusion, the auxiliary 4×4 region head (helps position-based queries, which ships often need), losses, frozen text encoder.

## Decision needed: training regime

| Option | Pros | Cons |
|---|---|---|
| Joint optical + SAR | PL-MoE stays justified; more data | Needs Thai text for optical data too |
| **SAR-only (lean)** | Less translation; ablating PL-MoE answers a question the paper left open | PL-MoE may become dead weight — which is itself a finding |
