---
type: literature-review
description: Lit review of SAR (synthetic aperture radar) visual grounding 2025–2026 — datasets, methods, SAR VLM/MLLM benchmarks — plus ranked thesis-gap candidates for the 4th-year project.
created: 2026-10-19
updated: 2026-10-19
---

# SAR Visual Grounding — Literature Review & Thesis Gaps

## TL;DR

- **Task:** given a SAR image + a text expression ("the largest ship near the dock"), output the box/mask of the referred target.
- **Field is tiny and young (2025→).** Dedicated SAR grounding = ~4 dataset/method lines; almost all are **single-class** (ships *or* towers) and **box-only**.
- **Strongest gap signals:**
  1. **Multi-target / generalized grounding** — MLLMs score ~80–90% single-target but ~60% multi-target on SARChat-Bench-2M.
  2. **No SAR referring *segmentation*** (text → mask) found.
  3. **No published SAR grounding numbers** for the multi-sensor RS-MLLMs (EarthDial, Earth-OneVision) — evaluated on SAR captioning/VQA only.
  4. **No grounding model uses SAR physics** (polarimetry / complex phase) — the physics and vision-language lines are separate.
- **Recommended thesis direction:** Gap 1 + 2 combined, with Gap 3 as the benchmark chapter (see [Thesis gaps](#thesis-gap-candidates-ranked)).

> **Verification status:** compiled from search results/abstracts on 2026-10-19; arXiv was not directly reachable, so full papers were **not read**. Dates for arXiv items are inferred from the ID (`YYMM.xxxxx`). Numbers marked *(snippet)* must be checked against the paper tables before citing.

## 1. Task taxonomy (where SAR grounding sits)

| Task | Input → Output | SAR status |
|---|---|---|
| REC / visual grounding | text → 1 box | ✅ Exists (TACMT, VGRSS, OptiSAR-Net++) |
| Generalized REC (GREC) | text → 0..N boxes | ⚠️ Early (SAAVG multi-class, multi-object) |
| Referring segmentation (RES) | text → mask | ❌ Not found |
| Region referring (inverse) | box → class/text | ✅ SARLANG-1M, SARChat-Bench-2M |
| Open-vocabulary detection | class names → boxes | ❌ No SAR-specific paper found |

## 2. Dedicated SAR grounding — datasets & methods

| Work | Venue / date | Dataset | Scale | Notes |
|---|---|---|---|---|
| **TACMT** — Text-aware cross-modal transformer | ISPRS JPRS, 2025 | **SARVG (towers)** a.k.a. SARVG1.0 | 2,465 imgs, 7,617 img–text pairs, **1 class** | Code + data released. Review reports +6.2% on SARVG1.0 *(snippet)* |
| **VGRSS** — Datasets & models for RS ship grounding | 2025 (repo Jan 2025) | **SARVG (ships)** from SAR-Ship-Dataset + optical RSSVG | ~43.8k imgs, ~54.4k objects *(per review table)* | Largest downloadable SAR grounding set |
| **Asymmetric Hierarchical Fusion** | Springer conf. chapter (year unverified) | **SAAVG** | multi-class, relational expressions, multi-object | Built on LQVG. Release "upon publication" — check link works |
| **OptiSAR-Net++** | arXiv 2603.24876 (Mar 2026) | **OptSAR-RSVG** | optical + SAR, 16 classes | Cross-domain RSVG task; SOTA on OptSAR-RSVG & DIOR-RSVG (claimed) |
| **TVLightFormer** | unverified (seen only in a reference list) | — | — | Lightweight language-guided target localization in SAR |

⚠️ **Name collision:** "SARVG" = towers (TACMT) **and** ships (VGRSS). Always cite the source paper.

## 3. SAR vision-language benchmarks & foundation models

| Work | Date | Grounding content | Key finding |
|---|---|---|---|
| **SARChat-Bench-2M** | arXiv 2502.08168 (Feb 2025) | Spatial grounding + referring, from SARDet-100K | Single-target: mPLUG-Owl3 >90%, most 80–85%; **multi-target ~60%** — authors call it open *(snippet)* |
| **SARLANG-1M** | arXiv 2504.03254 (Apr 2025) | Region referring only (box → class) | ~1.08M img–text pairs, 10 VLMs evaluated |
| **SAR-TEXT** | arXiv 2507.18743 (Jul 2025) | — | Image–text pretraining data (SAR-Narrator) |
| **FSAR-Cap** | arXiv 2510.16394 (Oct 2025) | — | Fine-grained captioning |
| **SARVLM** | arXiv 2510.22665 (Oct 2025) | Semantic localization (per snippet) | SAR VL foundation model |
| **SARCLIP** | ISPRS JPRS, 2025 | — | CLIP-style SAR–text contrastive pretraining; usable as grounding backbone |

## 4. Remote-sensing MLLMs — SAR coverage

| Model | SAR input? | SAR grounding evaluated? |
|---|---|---|
| GeoChat, SkySenseGPT | ❌ optical only | ❌ |
| GeoGround (2411.11904) | Not stated (trained on DIOR-RSVG) | ❌ |
| EarthGPT (2401.16822) | ✅ optical/SAR/IR | Not confirmed |
| EarthDial (CVPR 2025, 2412.15190) | ✅ 11.11M pairs incl. SAR | ❌ grounding only on RGB benchmarks |
| Earth-OneVision (2606.10819) | ✅ | ❌ SAR eval = SARLANG captioning/VQA only (VQA 80.68%) |

## 5. Adjacent: SAR physics line (not yet connected to language)

- **Complex-valued SAR foundation model** — IEEE TIP 2026 (arXiv 2504.11999): pretrains by predicting polarimetric scattering-basis coefficients.
- **CV-SSMNet** — arXiv 2607.19787: complex-valued state-space model on PolSAR coherency matrix with H/A/α, Freeman–Durden priors.
- **SARATR-X-v2** — arXiv 2607.23238: scale-aware SAR foundation-model pretraining.
- No paper found combining **physics features + language grounding**.

## 6. Recurring limitations across the field

| Limitation | Evidence |
|---|---|
| Single-class datasets | SARVG towers (1 class); SARVG ships (1 class); SAAVG paper explicitly states prior work is single-category |
| Box-only outputs | No RES dataset found |
| Templated / short expressions | Datasets derived from detection labels (SARDet-100K, SAR-Ship-Dataset) — expressions likely auto-generated *(verify per dataset)* |
| Incomparable results | Each paper reports on its own dataset |
| SAR treated as grayscale optical | Grounding models use amplitude images; phase/polarization unused |

## Thesis gap candidates (ranked)

Ranking = novelty × feasibility for a ~1-year undergrad CPE thesis.

| # | Gap | Novelty | Feasibility | Data source | Risk |
|---|---|---|---|---|---|
| **1** | **Generalized SAR grounding** — one expression → 0..N targets, incl. "no target" | High | **Medium–High** | Re-annotate SARDet-100K / SARVG-ships with multi-object + negative expressions (LLM-generated, human-checked) | SAAVG may overlap — read it first |
| **2** | **SAR referring segmentation** (text → mask) | **High** (none found) | Medium | Ship datasets with instance masks (e.g. HRSID — *verify mask availability*) + SAM-style mask head | Mask labels are the bottleneck |
| **3** | **Benchmark: general/RS MLLMs vs specialist models on SAR grounding** | Medium | **High** | Existing SARVG ships + towers + SARChat-Bench | Easiest; lower novelty alone — best as a chapter, not the whole thesis |
| 4 | Physics-aware grounding (polarimetric cues in text, e.g. "double-bounce structure") | Very high | Low | Needs SLC / PolSAR data + expert labels | Too much for one year unless advisor has SAR data |
| 5 | Lightweight / edge SAR grounding | Low–Med | High | Existing datasets | TVLightFormer already exists |
| 6 | Optical→SAR transfer for grounding | Low | Medium | DIOR-RSVG + SARVG | OptiSAR-Net++ (2026) already covers it |

### Recommendation

**Combine #1 + #2, validated with #3:** *"Generalized referring segmentation for SAR ship imagery"* —
1. Build a small dataset: multi-object + negative expressions over ship images that have masks.
2. Baselines: TACMT/VGRSS (box), a zero-shot RS-MLLM (EarthDial), and a SAM-based mask head.
3. Contribution: first SAR RES/GRES benchmark + one model improvement.

Why: two gaps with direct evidence, uses existing public images (no SAR acquisition needed), and #3 guarantees a result chapter even if the model doesn't beat baselines.

## Next actions

- [ ] Read **SAAVG** paper in full — confirm how much of Gap #1 it already covers.
- [ ] Read **OptiSAR-Net++** (newest) and its related-work section to catch papers missed here.
- [ ] Check **HRSID / SSDD** for instance-mask annotations (Gap #2 feasibility).
- [ ] Pull SARChat-Bench-2M referring/grounding tables to verify the 90% vs 60% numbers.
- [ ] Search IEEE TGRS / JSTARS / GRSL directly (web search under-covers IEEE).
- [ ] Pitch to a CV advisor — see [[cpe-thesis-advisors]] (Kharittha Jangsamsi, Naveed Sultan, Suthep Madarasmi list CV).

## Sources

- TACMT — https://www.sciencedirect.com/science/article/abs/pii/S0924271625000802
- VGRSS code/data — https://github.com/LwZhan-WUT/VGRSS
- Asymmetric Hierarchical Fusion (SAAVG) — https://link.springer.com/chapter/10.1007/978-981-92-0071-9_27
- OptiSAR-Net++ — https://arxiv.org/html/2603.24876
- RS visual grounding review (Electronics 2025) — https://www.mdpi.com/2079-9292/14/14/2815
- SARChat-Bench-2M — https://arxiv.org/pdf/2502.08168
- SARLANG-1M — https://arxiv.org/html/2504.03254
- SAR-TEXT — https://arxiv.org/pdf/2507.18743
- FSAR-Cap — https://arxiv.org/pdf/2510.16394
- SARVLM — https://arxiv.org/pdf/2510.22665
- SARCLIP — https://www.sciencedirect.com/science/article/abs/pii/S0924271625004058
- EarthGPT — https://arxiv.org/pdf/2401.16822
- EarthDial — https://arxiv.org/pdf/2412.15190
- Earth-OneVision — https://arxiv.org/pdf/2606.10819
- GeoGround — https://www.alphaxiv.org/abs/2411.11904
- RS-MLLM survey (domain vs general) — https://arxiv.org/pdf/2607.20284
- Complex-valued SAR foundation model — https://doi.org/10.1109/tip.2026.3652417
- CV-SSMNet (PolSAR) — https://arxiv.org/abs/2607.19787
- SARATR-X-v2 — https://arxiv.org/pdf/2607.23238
- SAR VLM overview (Sci China Inf Sci 2026) — https://files.sciengine.com/pdfs/1674-733X/AD4995BCD8044D07B38FE235D49C36F6.pdf
