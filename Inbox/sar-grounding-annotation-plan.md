---
type: project-plan
description: Annotation role plan for the SAR (Sentinel-1, Thai waters) visual grounding thesis — reading list, SSDD summary, 8-step pipeline, tile edge rule, AIS/GFW verification, OptiSAR-Net++ vs TACMT vs GREC, compute estimate.
created: 2026-11-11
updated: 2026-11-11
---

# SAR Grounding — Annotation & Language Queries Plan

Markers: ✅ verified (checked in code/paper text) · ⚠️ inferred/estimate (not verified). Broad literature + thesis-gap ranking: [[sar-visual-grounding-lit-review]]. Advisors: [[cpe-thesis-advisors]].

## TL;DR

- Project: find ships in Sentinel-1 SAR images of Thai waters from a text description. 5-person group; owner = **Annotation & Language Queries**.
- Main contribution = **Thai SAR grounding dataset with multi-target and no-target labels**. 3 objectives: Thai dataset, multi/no-target model, evaluation on clean + Thai test sets. Edge devices out of scope. Committee (Aj. Musi, Aj. Aung) wants one chain: problem → gap → solution → evidence.
- Annotation is now MORE central; ~80% of the reading list survives any topic change. Read it now.
- Pipeline: 8 steps (§3); novelty = steps 4–6 (verify, describe, cross-check).
- Decided: descriptions = LLM draft → human edit; tile = 640; main baseline = OptiSAR-Net++ (pending Kritipoom).
- Undecided: tile edge rule (option C recommended, §4).
- Unchanged OptiSAR-Net++ would score 0% on no-ship queries (top-1 output) — small fix: confidence threshold (§6).

| Role | Person |
|---|---|
| Annotation & Language Queries | Jedsarid Sangsuwan (owner) |
| Model Design | Nattawat Ruensumrit |
| Sentinel-1 data pipeline & web demo | Kittithat Wongsod |
| Evaluation & reliability | Nattaphat Jaroenpeerapamorn |
| Baselines & training | Kritipoom Chanla |

## 1. Owner's reading list (annotation role)

Verdict: yes, read now. 25-paper group list exists (5 per member).

| Order | Paper | Survives topic change? | Read only | Link |
|---|---|---|---|---|
| 1 | SSDD official release (Zhang et al., Remote Sensing 2021) core | Any SAR ship work, even if text part dropped | Box rules, size definition, mistakes of earlier datasets | https://www.mdpi.com/2072-4292/13/18/3690 |
| 2 | GRES (Liu, Ding, Jiang, CVPR 2023) — REPLACES GREC for annotation | Defines how gRefCOCO multi/no-target expressions were collected | Dataset-collection section | arXiv ID believed 2306.00968 (⚠️ verify) |
| 3 | ReferItGame (Kazemzadeh et al., EMNLP 2014) | Always (QC: one writes, another must find) | Game mechanics | https://aclanthology.org/D14-1086/ |
| 4 | Pervasive Label Errors in Test Sets (Northcutt et al., NeurIPS 2021) | Always (argues for double-checked test set) | Main finding + one figure | https://arxiv.org/abs/2103.14749 |
| 5 | RefCOCO (Yu et al., ECCV 2016) core | Unless text part dropped | Expression collection + splits | https://arxiv.org/abs/1608.00272 |
| 6 | RefCOCOg (Mao et al., CVPR 2016) | Partly — its "exactly one object" rule conflicts with multi/no-target; use only for "write clearly" rules | Writing rules | https://arxiv.org/abs/1511.02283 |

From teammates' lists:

| Paper | Use | Link |
|---|---|---|
| GREC | Metric | https://arxiv.org/abs/2308.16182 |
| xView3-SAR | AIS-assisted labeling | https://arxiv.org/abs/2206.00897 |
| RSVG | How DIOR-RSVG expressions were generated (⚠️ believed semi-automatic, unverified) | https://arxiv.org/abs/2210.12634 |

Correction: GREC paper has NO dataset-construction section; Sec 2.2 says "Please kindly refer to GRES [22]" → GRES is the annotation reference.

## 2. SSDD summary (✅ read in full from the PDF)

| Item | Content |
|---|---|
| Problem | 2017 SSDD had dirty labels (missed ships, false ships, non-compact boxes) and ambiguous usage rules → unfair comparisons |
| Method | Relabeled all ships in 3 forms: BBox-SSDD, RBox-SSDD (rotated), PSeg-SSDD (polygons via LabelMe); strict usage standards |
| Data | 1,160 images, 2,456 ships; RadarSat-2, TerraSAR-X, Sentinel-1; 1–15 m; HH/VV/VH/HV; Yantai (China), Visakhapatnam (India). Widths 214–668 px, heights 160–526 px; many 500 wide |
| Key number | 46.59% of 161 DL SAR ship-detection papers (75) used SSDD |

Reusable rules:
- Test = filenames ending 1 or 9 → 928 train / 232 test (8:2).
- Inshore = image contains any land (test: 46 inshore / 186 offshore).
- Size thresholds from own histogram, rejecting COCO 32²/96²: BBox small <1000 px², medium 1000–8000, large >8000; RBox/PSeg small <625.
- Hard subsets: 10 dense-small-ship test images; parallel-berthing-at-port subset.
- Polygon → BBox via min/max; → RBox via `cv2.minAreaRect`. VOC + COCO formats; grayscale copied to 3 channels.

Limitations:
- No QC protocol (only "with the participation of many researchers, we re-label…"; no annotator agreement / double-check).
- ⚠️ Inferred: filename split likely leaks neighbouring crops of the same scene (only 2 locations).
- Average ship ~35×35 px vs Sentinel-1 2–3 px ships; authors say Sentinel-1 ships are "universally small, with unclear geometric features" → supports committee comment 7 (why a Thai dataset).

Link to project: split/size/inshore/density rules double as attributes for generating multi/no-target expressions.

## 3. Annotation pipeline (8 steps)

Flow (owner will draw the diagram): 1 Scene (Kittithat) → 2 Tiles (Kittithat) → 3 Draw boxes (owner) → 4 Verify ships (owner) → 5 Write descriptions (owner) → 6 Cross-check (owner; fail loops back to 5) → 7 Split (owner + Nattaphat) → 8 Export + validate (owner) → hand-off to Kritipoom (training) and Nattaphat (evaluation).

| # | Step | Plain words | Backed by |
|---|---|---|---|
| 1 | Get scene | Download Sentinel-1 GRD, calibrate, denoise, dB, stretch 0–255 (fix before labeling) | Filipponi 2019 |
| 2 | Tile | 640×640 tiles (OptiSAR-Net++ input), ~64 px overlap; never downscale | OptiSAR-Net++ code |
| 3 | Boxes | Box every ship in original pixel coords; edge rule (§4) | SSDD |
| 4 | Verify | Match to GFW Sentinel-1 detections → HIGH/MEDIUM/LOW; store verification source per label | xView3-SAR |
| 5 | Descriptions | DECIDED: LLM drafts → human edits. Types: single-target, multi-target ("all ships berthed at the pier"), no-target. Refer only to what is inside the tile | RefCOCO, GRES/GREC |
| 6 | Cross-check | A writes, B finds without seeing answer; mismatch → rewrite; test set checked twice | ReferItGame, Northcutt |
| 7 | Split | By location or date, not random; overlapping/neighbouring tiles in same split | SSDD, Barz & Denzler |
| 8 | Export | COCO JSON + YOLO .txt in OptiSAR-Net++ layout (`sar_000001.jpg` ↔ `sar_000001.txt`); run its `scripts/validate_dataset.py` | OptiSAR-Net++ repo |

Highlight on diagram: steps 4–6 (prior SAR grounding datasets don't describe these).

## 4. Edge rule (undecided — option C recommended)

Problem: ships crossing tile borders. Matters more for grounding: a half-cut ship makes a "no ship" description wrong.

⚠️ Estimated crossing chance (10 m pixels, 640 tiles):

| Ship | Length | ≈ px | Crossing chance |
|---|---|---|---|
| Fishing boat | ~30 m | ~3 | ~1% |
| Cargo | ~200 m | ~20 | ~6% |
| Tanker | ~350 m | ~35 | ~11% |

Rare overall but hits big port ships.

| Option | Rule | Note |
|---|---|---|
| A | Center-point inside | Simple |
| B | Area threshold | ✅ Ultralytics `split_dota.py` keeps object if ≥70% inside (`iof_thr=0.7`, 200 px gap on 1024 crops) |
| C (rec.) | Overlap tiles ~64 px; ≥70% keep / 30–70% "ignore" / <30% drop; overlapping tiles same split | Never write no-target/all-ships descriptions contradicting an ignored ship |

Open: does OptiSAR-Net++ training respect COCO `iscrowd` as ignore? Unchecked. Fallback: drop 30–70% ships and skip no-target/all-ships descriptions for those tiles.

## 5. Ship verification via AIS (⚠️ mostly from search snippets, not opened pages)

Best option: **Global Fishing Watch (GFW) Sentinel-1 SAR vessel detections** (Paolo et al., Nature 2024). Free non-commercial (CC BY-NC 4.0), 2017 to ~5 days ago, vessels >~10 m, each flagged AIS-matched or not. Data Download Portal or API dataset `public-global-sar-presence`.

| Match result (blob within 1–2 px, same scene) | Confidence |
|---|---|
| AIS-matched | HIGH |
| Detected, no AIS | MEDIUM |
| No match | LOW → 2 annotators check VV+VH + Sentinel-2/Google Earth; remove rocks, platforms, aquaculture |

Not usable:

| Source | Why |
|---|---|
| GFW AIS API | Free but gridded presence-hours; raw tracks unconfirmed |
| MarineTraffic / Spire / Kpler | Paid; Spire ESA route only ESA states + Canada |
| AISHub | Must contribute a receiver |
| EMSA / Copernicus | Closed to universities |
| Thai DOF VMS | >30 GT fishing only, hourly, no researcher route found |
| NOAA MarineCadastre | US only |

Caveats:
- GFW estimates 72–76% of industrial fishing vessels not publicly tracked, concentrated in S/SE Asia → small Thai boats mostly lack AIS.
- GFW excludes near-shore areas (distance unknown) → ports/Chao Phraya may be missing.
- Unmatched blob = "unverified", not "dark vessel".
- Other datasets: LS-SSDD-v1.0 used SAR experts + AIS + Google Earth; HRSID Google Earth; SSDD manual only.

Action: Kittithat registers a GFW account and checks coverage of actual scenes/dates.

## 6. Models: TACMT vs OptiSAR-Net++ vs GREC vs SARATR-X (✅ verified in repos unless marked)

| | TACMT | OptiSAR-Net++ | GREC | SARATR-X |
|---|---|---|---|---|
| What | Grounding model (ISPRS 2025) | Grounding model + OptSAR-RSVG dataset (arXiv 2603.24876, 2026) | Task definition + gRefCOCO + metric (no new model) | Image-only SAR foundation backbone (HiViT, self-supervised, 0.18M SAR images); no text input |
| Input | 512×512 (long side resize, pad; train random 320–512) | 640×640 letterbox (`imgsz=640` hard-coded) | n/a | n/a |
| Boxes/query | exactly 1 (`num_queries=1`) | many scored, but `scripts/evaluate.py` keeps top-1 (`conf.argmax()`) | 0..N via confidence threshold | n/a |
| Repo | github.com/CAESAR-Radi/TACMT (PyTorch 1.9.1) | github.com/JunDong-dev/OptiSAR-Net-PlusPlus (code; data on Hugging Face; weights released) | github.com/henghuiding/gRefCOCO | github.com/waterdisappear/SARATR-X |

GREC metrics and results:
- Pr@(F1=1, IoU≥0.5): sample correct only if all targets found and no extra boxes. N-acc: no-target accuracy.
- GREC Table 2: top-1/top-k → 0.0 Pr and 0.0 N-acc; threshold 0.5 → 37.0/32.2; 0.9 → 51.2/45.7.
- Classic REC models ~85% on RefCOCO drop to ~28–58% on gRefCOCO.
- GREC notes UNINEXT was pretrained on val/test images (leakage) and retrained without them.
- Implication: unchanged OptiSAR-Net++ scores 0% on no-ship descriptions; switching top-1 → threshold is a small change. Pick threshold on validation, never test. GREC = "rules of the exam", not a technique (only technique: threshold selection). Our contribution = dataset + task on SAR, not a new technique.

OptiSAR-Net++ training defaults that hurt this data (Ultralytics defaults not overridden; ⚠️ from code reading, confirm by plotting a batch):

| Default | Problem | Fix |
|---|---|---|
| Random scale 0.5 | Ships can shrink to ~1 px | Lower to ~0.1 |
| `fliplr=0.5` | No direction-word swap in text (left↔right list only for adversarial negatives) | `fliplr=0` or swap words |
| `mosaic=1.0` | Can crop out description context, breaks multi/no-target | `--mosaic 0` |

OptSAR-RSVG dataset:
- 46,825 images / 90,148 annotations / 16 categories; train 37,957 / val 4,434 / test 4,434. Released split differs from paper's.
- Merges RSVGD/RSSVG, OPT-RSVG, SARVG (ships, from SAR-Ship-Dataset via VGRSS) and SARVG1.0 (towers, from TACMT); GPT-4o rewrote descriptions.
- README order: augmentation (flips/180° rotations of minority classes, +9,046 images) in stage 2 BEFORE splitting in stage 3 → ⚠️ possible flipped-copy leakage into test (not checked) → task for Nattaphat.

SARATR-X: pretraining set includes SAR-Ship-Dataset (39,729), SSDD, HRSID → testing a SARATR-X backbone on SARVG ships = backbone saw test images (unlabeled) → leakage; test only on Thai data.

Name clash: "SARVG" = towers (TACMT, a.k.a. SARVG1.0) AND ships (VGRSS).

## 7. Comparison experiment plan (TACMT vs OptiSAR-Net++ vs SARATR-X)

Verdict: TACMT vs OptiSAR-Net++ on the same dataset = good (committee comment 5). SARATR-X cannot be a third competitor (no text) → optional experiment B: swap it in as OptiSAR-Net++ backbone (high engineering cost: HiViT/MMDetection vs YOLO-style CNN), tested only on Thai data.

Fairness rules:
- Same split; train/fine-tune both on it. Don't use OptiSAR released weights on SARVG: its training split may contain SARVG test images (⚠️ inferred; check by image hashes).
- Same input 640 (TACMT has commented-out 640 configs).
- Report classic Pr@0.5 AND GREC Pr@(F1=1) + N-acc.
- 3 seeds, mean ± spread (Bouthillier et al.).
- Threshold chosen on val; same augmentation for both.

| Order | Experiment |
|---|---|
| 1 (now) | A: both models on SARVG ships |
| 2 (after Thai dataset) | A on Thai data with GREC metrics (main result) |
| 3 (optional) | B: SARATR-X backbone |

Pending decision: drop SARATR-X from main comparison; tell Nattawat it fits experiment B.

## 8. Compute estimate — OptiSAR-Net++ retrain from zero on the weakest GPU

Cluster (Slurm): weakest = RTX 3060 12 GB (GPU02 has 2×). Others: RTX 4090 (GPU01, GPU06), A4000, 4070 Ti, 3080 (10 GB, less VRAM), 2× L40 (GPU07, GPU08).

✅ Facts: 37,957 train images × 300 epochs ≈ 11.4M images; paper used 8× RTX 4090, global batch 64 (8/GPU); code accumulates gradients to nominal batch 64 (`nbs=64`), so `--batch 8` on a 3060 keeps the same effective batch.

⚠️ Estimate (assumed 15–35 img/s on a 3060):

| Throughput | Time (1× 3060) |
|---|---|
| 35 img/s | ~3.8 days |
| 25 img/s | ~5.3 days |
| 15 img/s | ~8.8 days |
| Both 3060s | ~2.5–5 days |

Measure instead: `python scripts/train.py --dataset-root datasets/OptSAR-RSVG --device 0 --batch 8 --workers 8 --dry-run --project runs/reproduce --name speedtest_3060` (1% data, 1 epoch); total seconds = 11.4M ÷ img/s; OOM → `--batch 4`.

Risks: Slurm job time limits (24–72 h typical) → chain jobs with `--resume last.pt`; shared-cluster etiquette.

| Cheaper path | Cost |
|---|---|
| Evaluate released weights | <1 h |
| Fine-tune on Thai data (~3,000 tiles × 100 epochs ≈ 300k images) | ~3 h at 25 img/s |
| Fair threshold comparison, 3 seeds each | ~1 day |
| Full reproduction | Only if committee demands it |

Next: Kritipoom runs the speed test on one RTX 3060.

## 9. Annotation rules carried forward (checklist)

- Label in original pixel coordinates.
- Descriptions reference only what is inside the tile.
- Overlapping tiles in the same split.
- Fix dB conversion/clipping before labeling.
- Keep descriptions short (MobileCLIP2 text encoder; CLIP-style 77-token limit ⚠️ unconfirmed for MobileCLIP2).
- Category names with modality prefix per OptSAR-RSVG.
- Channel option [VV, VH, VV/VH] ⚠️ untested idea.
- Store verification source per label.

## 10. Decisions log + open questions

| Date | Decision |
|---|---|
| 2026-11-11 | Description method = LLM draft → human edit |
| 2026-11-11 | Main baseline = OptiSAR-Net++ (pending Kritipoom confirmation) |
| 2026-11-11 | Tile = 640 |

Open questions / backlog:
- [ ] Edge rule option C (and `iscrowd` support in training)
- [ ] GFW coverage of actual scenes/dates (Kittithat)
- [ ] Drop SARATR-X from main comparison; tell Nattawat
- [ ] Check OptSAR-RSVG flipped-copy leakage (Nattaphat)
- [ ] Verify GRES arXiv ID
- [ ] RTX 3060 speed test (Kritipoom)
