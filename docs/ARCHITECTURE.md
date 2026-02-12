# 🏗️ Model Architecture

> DINOv3-ViT-L/16 + ViT-Adapter + Mask2Former for Semantic Segmentation

## 🔄 Pipeline Overview

```
Input Image (720×720 RGB)
        │
        ▼
┌─────────────────────────┐
│  DINOv3-ViT-L/16        │  🔒 Frozen (~1B params)
│  (HuggingFace pretrained)│  Extracts features at layers [4, 11, 17, 23]
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  DINOv3_Adapter          │  🔓 Trainable (~50M params)
│  (ViT-Adapter)           │  Converts single-scale → multi-scale FPN
└─────────┬───────────────┘
          │  Outputs: 4-level feature pyramid
          │  f1: H/4  (180×180, 1024ch)
          │  f2: H/8  (90×90,   1024ch)
          │  f3: H/16 (45×45,   1024ch)
          │  f4: H/32 (22×22,   1024ch)
          ▼
┌─────────────────────────┐
│  Mask2Former Head        │  🔓 Trainable
│  (Pixel Decoder +        │  Universal segmentation head
│   Transformer Decoder)   │  Outputs per-mask + per-class predictions
└─────────┬───────────────┘
          │
          ▼
   Segmentation Map (7 classes)
```

---

## 🧠 Component 1: DINOv3 Backbone

**Model:** `facebook/dinov3-vitl16-pretrain-sat493m`

| Property | Value |
|----------|-------|
| Architecture | Vision Transformer (ViT-Large) |
| Patch size | 16×16 |
| Layers | 24 |
| Embedding dim | 1024 |
| Attention heads | 16 |
| Parameters | ~1B |
| Status | **Frozen** (no gradients) |

**What it does:**
- Takes the input image and splits it into 16×16 patches
- For 720×720 input → 45×45 = 2,025 patches (+1 CLS token + 4 register tokens)
- Processes through 24 transformer layers
- Features are **extracted at layers [4, 11, 17, 23]** (the interaction indexes)

**Code:** `dinov3_mask2former_integration.py` → `DINOv3AdapterBackbone`

---

## 🔧 Component 2: DINOv3_Adapter (ViT-Adapter)

The adapter is the **key innovation** — it converts ViT's single-scale token output into a multi-scale feature pyramid that Mask2Former expects.

**Code:** `models/backbone/dinov3_adapter.py` → `DINOv3_Adapter`

### Sub-components:

### 2a. Spatial Prior Module (SPM)
```
Input Image (B, 3, H, W)
    │
    ├─→ Stem: 3× Conv+BN+ReLU + MaxPool → (B, 64, H/4, W/4)
    │
    ├─→ Conv2: → (B, 128, H/8, W/8)   → FC → c2 (B, N2, 1024)
    ├─→ Conv3: → (B, 256, H/16, W/16)  → FC → c3 (B, N3, 1024)
    └─→ Conv4: → (B, 256, H/32, W/32)  → FC → c4 (B, N4, 1024)
```
- Generates **spatial features** at 3 scales directly from the image
- These act as "spatial priors" that complement the ViT's semantic features

### 2b. Interaction Blocks (×4)
```
For each interaction_index [4, 11, 17, 23]:
    1. Get ViT features at that layer
    2. Multi-Scale Deformable Attention between spatial priors and ViT features
    3. Convolutional FFN for feature refinement
    4. Layer Norm + Residual connection
```
- **Deformable attention** efficiently attends across multiple scales
- Each block uses `n_points=4` sampling points per attention head
- `deform_num_heads=16` attention heads

### 2c. Feature Fusion & Output
```
After all interaction blocks:
    Split refined features → c2, c3, c4
    Add ViT features (with interpolation) to each scale
    Apply BatchNorm
    Upsample c2 → f1 (H/4 scale)
    Output: {"1": f1, "2": f2, "3": f3, "4": f4}
```

### Adapter Config

| Parameter | Value | Description |
|-----------|-------|-------------|
| `interaction_indexes` | [4, 11, 17, 23] | Which ViT layers to tap into |
| `conv_inplane` | 64 | SPM conv channels |
| `n_points` | 4 | Deformable attention sampling points |
| `deform_num_heads` | 16 | Deformable attention heads |
| `drop_path_rate` | 0.3 | Stochastic depth rate |
| `with_cp` | True | Gradient checkpointing (saves memory) |

---

## 🎭 Component 3: Mask2Former

**Base config from:** `facebook/mask2former-swin-base-coco-panoptic`

The Mask2Former head is a **universal segmentation architecture** that works for panoptic, instance, and semantic segmentation.

### How it works:
1. **Pixel Decoder:** FPN-style fusion of the 4-level feature pyramid → high-res features
2. **Transformer Decoder:** Masked cross-attention with learnable object queries
3. **Prediction Heads:**
   - `masks_queries_logits` — per-query binary mask predictions
   - `class_queries_logits` — per-query class predictions

### Modified for this project:
- `num_labels = 7` (LoveDA classes)
- `backbone_config` replaced with custom `DINOv3AdapterBackboneConfig`
- `backbone` replaced with `DINOv3AdapterBackbone`
- Feature strides: `[4, 8, 16, 32]`

---

## 📏 Resolution & Patch Math

| Input Size | Patches per side | Total patches | f1 (H/4) | f2 (H/8) | f3 (H/16) | f4 (H/32) |
|------------|-----------------|---------------|-----------|-----------|------------|------------|
| 720×720 | 45 | 2,025 | 180×180 | 90×90 | 45×45 | 22×22 |
| 1024×1024 | 64 | 4,096 | 256×256 | 128×128 | 64×64 | 32×32 |

> ⚠️ Input size must be divisible by 16 (DINOv3 patch size)

---

## 🧊 Parameter Breakdown

| Component | Parameters | Trainable? |
|-----------|-----------|------------|
| DINOv3-ViT-L/16 | ~1B | ❄️ No (frozen) |
| Spatial Prior Module | ~5M | ✅ Yes |
| Interaction Blocks | ~30M | ✅ Yes |
| Fusion layers | ~15M | ✅ Yes |
| Mask2Former head | ~40M | ✅ Yes |
| **Total trainable** | **~90M** | |

---

## 🔗 Key Files

| File | Contains |
|------|----------|
| `models/backbone/dinov3_adapter.py` | `DINOv3_Adapter`, `SpatialPriorModule`, `InteractionBlockWithCls`, `Extractor`, `ConvFFN`, `DWConv` |
| `models/utils/ms_deform_attn.py` | `MSDeformAttn`, `MSDeformAttnFunction` |
| `dinov3_mask2former_integration.py` | `DINOv3AdapterBackbone`, `DINOv3AdapterBackboneConfig`, `create_dinov3_mask2former()` |
| `dinov2_mask2former_integration.py` | Same structure but for DINOv2-ViT-B/14 |
