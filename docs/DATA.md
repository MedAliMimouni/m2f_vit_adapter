# 📦 Data Pipeline

> LoveDA dataset loading, preprocessing, and class definitions

## 🗺️ LoveDA Dataset

**LoveDA** is a multi-scale land-use/land-cover dataset containing satellite imagery from rural and urban areas.

### Directory Structure
```
/mnt/biontech/temp_mimouni/LoveDA/
├── Train/
│   ├── Rural/
│   │   ├── images_png/    ← RGB satellite images
│   │   └── masks_png/     ← Segmentation masks (grayscale)
│   └── Urban/
│       ├── images_png/
│       └── masks_png/
├── Val/
│   ├── Rural/{images_png, masks_png}
│   └── Urban/{images_png, masks_png}
└── Test/
    ├── Rural/{images_png, masks_png}
    └── Urban/{images_png, masks_png}
```

> ⚠️ The dataset path is configured in `conf/data/loveda.yaml` → `data.dataset_root`

---

## 🏷️ Classes (7 total)

| ID | Class | Color (RGB) | Swatch |
|----|-------|-------------|--------|
| 0 | Background | (128, 128, 128) | ⬜ Gray |
| 1 | Building | (255, 0, 0) | 🟥 Red |
| 2 | Road | (0, 255, 0) | 🟩 Green |
| 3 | Water | (0, 0, 255) | 🟦 Blue |
| 4 | Barren | (255, 255, 0) | 🟨 Yellow |
| 5 | Forest | (255, 0, 255) | 🟪 Magenta |
| 6 | Agriculture | (0, 255, 255) | 🩵 Cyan |

### Metric handling:
- **`val_mean_iou`** — includes all 7 classes (background + 6 semantic)
- **`val_mean_iou_no_bg`** — excludes background (class 0), averages over classes 1–6

---

## 🔄 Data Loading Pipeline

### Code: `data.py`

### 1. Dataset Class: `LoveDADataset`

```python
from data import LoveDADataset, create_dataloaders, collate_fn

# Create dataset directly
dataset = LoveDADataset(
    root_dir="/mnt/biontech/temp_mimouni/LoveDA/Train",
    processor=processor,        # HuggingFace AutoImageProcessor
    image_size=720,
    transform=None              # Optional custom transforms
)

# Access a sample
sample = dataset[0]
# Returns: {
#   "pixel_values": tensor (3, 720, 720),
#   "mask_labels":  list of tensors (per-class binary masks),
#   "class_labels": tensor of class IDs present
# }
```

### 2. DataLoader Factory: `create_dataloaders()`

```python
train_loader, val_loader, test_loader = create_dataloaders(
    dataset_root="/mnt/biontech/temp_mimouni/LoveDA/",
    processor=processor,
    image_size=720,
    batch_size=8,
    num_workers=4
)
```

### 3. Custom Collation: `collate_fn()`

Handles variable-length masks per sample:
- `pixel_values` → stacked into `(B, 3, H, W)` tensor
- `mask_labels` → kept as list of lists (variable per sample)
- `class_labels` → kept as list of tensors (variable per sample)

---

## 🖼️ Preprocessing

Uses HuggingFace `AutoImageProcessor` (from Mask2Former):

| Step | Details |
|------|---------|
| Resize | To configured `image_size` (720 or 1024) |
| Normalize | ImageNet mean/std |
| Mask processing | Converts segmentation map → per-class binary masks |
| Label reduction | `do_reduce_labels=True` in processor config |

### Processor initialization (in `dinov3_mask2former_integration.py`):
```python
processor = AutoImageProcessor.from_pretrained(
    "facebook/mask2former-swin-base-coco-panoptic"
)
processor.do_reduce_labels = True
processor.ignore_index = 0       # Background / no-data
processor.size = {"height": 720, "width": 720}
processor.num_labels = 7
```

---

## 📏 Resolution Options

| Config | Image Size | Patches (DINOv3 p=16) | Memory |
|--------|-----------|----------------------|--------|
| `data: loveda` | 720×720 | 45×45 = 2,025 | Normal |
| `data: loveda_1024` | 1024×1024 | 64×64 = 4,096 | Higher |

### Switch between them:
```bash
# Default 720×720
python train_hydra.py

# High-res 1024×1024
python train_hydra.py --config-name=config_1024

# Custom size (must be divisible by 16)
python train_hydra.py data.image_size=512
```

---

## 🔗 Key Files

| File | Contains |
|------|----------|
| `data.py` | `LoveDADataset`, `collate_fn`, `create_dataloaders()` |
| `conf/data/loveda.yaml` | Data config (720×720) |
| `conf/data/loveda_1024.yaml` | Data config (1024×1024) |
