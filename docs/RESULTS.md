# 📊 Training & Evaluation Results

> Summary of all training runs and their outcomes

---

## 🧪 Run 1: DINOv3-ViT-L/16 (Early Training)

**Source:** `training_results.json`

| Property | Value |
|----------|-------|
| Model | DINOv3-ViT-L/16 + Mask2Former |
| Dataset | LoveDA |
| Image size | 720×720 |
| Batch size | 8 |
| Interaction indexes | [4, 11, 17, 23] |
| Patches | 45×45 = 2,025 per image (+ 5 special tokens) |

### Metrics
| Metric | Value |
|--------|-------|
| **Best val mIoU (semantic)** | **0.1175** |
| Note | Excluding background, early training |

> ⚠️ This appears to be from an early/incomplete training run. More epochs needed.

---

## 🧪 Run 2: DINOv2-ViT-B/14 (Full Training — 48 epochs)

**Source:** `evaluation_results/`

| Property | Value |
|----------|-------|
| Model | DINOv2-ViT-B/14 + Mask2Former |
| Checkpoint | `dinov2-mask2former-loveda-epoch=48-val_mean_iou=0.29.ckpt` |
| Dataset | LoveDA Val split |
| Total pixels evaluated | 33,541,919 |

### Overall Metrics

| Metric | Value |
|--------|-------|
| **Mean IoU (all classes)** | **0.2711** |
| Accuracy | 0.4350 |
| F1-Score (macro) | 0.3934 |
| Weighted accuracy | 0.5700 |

### Per-Class Breakdown

| Class | Precision | Recall | F1 | IoU | Assessment |
|-------|-----------|--------|------|------|-----------|
| Background | 0.00 | 0.00 | 0.00 | 0.0000 | ❌ Not learned |
| Building | 0.52 | 0.92 | 0.67 | 0.5007 | ✅ Good |
| Road | 0.48 | 0.23 | 0.31 | 0.1834 | ⚠️ Under-detected |
| Water | 0.47 | 0.49 | 0.48 | 0.3158 | 🟡 Moderate |
| Barren | 0.22 | 0.11 | 0.15 | 0.0804 | ❌ Poor |
| Forest | 0.37 | 0.66 | 0.48 | 0.3146 | 🟡 Moderate |
| Agriculture | 0.72 | 0.63 | 0.67 | 0.5028 | ✅ Best class |

### Analysis

🏆 **Best performers:**
- **Agriculture** (IoU 0.50): Largest class, well-balanced precision/recall
- **Building** (IoU 0.50): High recall (92%) but tends to over-predict

⚠️ **Worst performers:**
- **Background** (IoU 0.00): Not learned at all (expected with `do_reduce_labels`)
- **Barren** (IoU 0.08): Very low recall (11%), often confused with other classes
- **Road** (IoU 0.18): Low recall (23%), thin linear features are hard

💡 **Key observations:**
- Building has very high recall (0.92) but lower precision (0.52) → over-segmentation
- Agriculture dominates the dataset (17.7M pixels) → model biased toward it
- Smaller classes (barren, road) underperform → class imbalance issue

---

## 📈 Training Log Versions

Located in `logs/`:

### DINOv3 runs (10 versions: v0–v9)
```
logs/dinov3_mask2former_loveda/version_0..9/
logs/dinov3_mask2former_loveda_csv/version_0..8/
```

### DINOv2 runs (12 versions: v0–v11)
```
logs/dinov2_mask2former_loveda/version_0..11/
```

### View with TensorBoard:
```bash
tensorboard --logdir logs/
```

---

## 🎯 Potential Improvements

Based on results analysis:

1. **Class imbalance** — Try class-weighted loss or focal loss
2. **Barren/Road underperformance** — Data augmentation (rotation, flip) for thin features
3. **More epochs for DINOv3** — The 0.1175 mIoU suggests early stopping; DINOv2 reached 0.27 at epoch 48
4. **Higher resolution** — Try 1024×1024 for better detection of small features (roads)
5. **Learning rate warmup** — Current setup jumps straight in; warmup could help stability
