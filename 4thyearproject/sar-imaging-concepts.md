---
type: concept-note
description: SAR background for defending the thesis — synthetic aperture and why SAR has no frame rate, revisit time vs multi-temporal imagery, why co-registered optical+SAR pairs fail for ships, speckle and small targets, and CNN vs Transformer long-range modelling.
created: 2026-11-11
updated: 2026-11-11
---

# SAR Imaging Concepts (for the defense)

Part of [[sar-thesis-hub]]. Explains limitations in [[optisar-net-plusplus]] and constraints in [[encoder-swap-experiment-plan]].

## TL;DR

- SAR builds one image from the satellite's motion, so there is **no frame rate**. "Temporal" in RS papers means scenes days apart.
- Ships **move between acquisitions**, so co-registered optical+SAR pairs are a poor fit for ship grounding.
- SAR ships are small, speckled blobs, so tight boxes (IoU ≥ 0.9) are hard to localize **and** hard to label.

## Why SAR has no frame rate

SAR = **Synthetic Aperture** Radar. A small antenna gives poor resolution, so the satellite sends pulses along a stretch of its orbit and combines the returns into one very long virtual antenna. The platform's motion is **part of forming the image**: one image is several seconds of flight, already combined.

| | Video | Multi-temporal SAR |
|---|---|---|
| Interval | ~33 ms (30 fps) | Days to weeks |
| Example | — | Sentinel-1 revisit ~6–12 days depending on satellites in operation |
| Use | Motion | Change detection |

New commercial constellations (ICEye, Capella, Synspective) reach sub-hour **revisit**, which is a scheduling property, not a frame rate.

## Why co-registered optical+SAR pairs fail for ships

- Optical and SAR images of the same area are usually taken **hours to days apart** from different satellites, and the ship has moved.
- Optical is unusable under cloud — which is when SAR matters most in SE-Asian monsoon conditions.
- Pair-based fusion works for **static** targets (buildings, land cover). [[optisar-net-plusplus]] uses unpaired data for this reason.

## Speckle and small targets

- **Speckle:** granular noise from coherent radar returns; it blurs object edges.
- SAR ships in OptSAR-RSVG are mostly small-to-medium in size. On a 20-px box, a 1–2 px error already fails IoU 0.9.
- So a Pr@0.9 gap can come from the model, from imprecise labels, or from object size. [[encoder-swap-experiment-plan]] change #4 separates the size effect.

## CNN vs Transformer — long-range dependency

| | Transformer | CNN + CLIP matching (OptiSAR-Net++) |
|---|---|---|
| Relating distant regions | Self-attention: every patch sees every patch | Local convolutions; range grows with depth |
| Cost | Quadratic in tokens | Linear, so fast and edge-friendly |
| Risk | Heavy | May plateau on larger, more relational datasets (their §VI hedge) |

Example where it matters: "the ship to the left of the second dock" relates two far-apart regions.
