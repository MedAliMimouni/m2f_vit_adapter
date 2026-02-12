# 🏋️ Training Guide

> How to train DINOv3 + Mask2Former on LoveDA

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements_hydra.txt
```

### 2. Set your HuggingFace token
```bash
source env.sh
# OR
export HF_TOKEN="your_token_here"
```

### 3. Train with defaults (720×720, 50 epochs)
```bash
python train_hydra.py
```

That's it! 🎉

---

## 📋 Usage Examples

### Quick test (1 epoch, for debugging)
```bash
python train_hydra.py training=quick_test
```

### High-resolution training (1024×1024)
```bash
python train_hydra.py --config-name=config_1024
```

### Custom hyperparameters
```bash
python train_hydra.py \
  training.max_epochs=100 \
  training.learning_rate=1e-4 \
  data.batch_size=4
```

### Lower batch size (if GPU OOM)
```bash
python train_hydra.py data.batch_size=2
```

### View the full resolved config (dry run)
```bash
python train_hydra.py --cfg job
```

---

## 🔄 Training Pipeline

### What happens when you run `train_hydra.py`:

```
1. Hydra loads config from conf/
       │
2. Creates run directory: runs/{timestamp}_{image_size}/
       │
3. create_dinov3_mask2former() builds the model:
   ├── DINOv3-ViT-L/16 backbone (frozen)
   ├── DINOv3_Adapter (trainable)
   └── Mask2Former head (trainable)
       │
4. create_dataloaders() loads LoveDA:
   ├── Train split (Rural + Urban)
   └── Val split (Rural + Urban)
       │
5. PyTorch Lightning Trainer runs:
   ├── Training loop (forward → loss → backward → step)
   ├── Validation every epoch (mIoU computation)
   ├── Checkpoint saving (top 3 by val_mean_iou_no_bg)
   └── LR scheduling (ReduceLROnPlateau)
       │
6. Outputs saved to:
   ├── runs/{timestamp}/checkpoints/*.ckpt
   ├── runs/{timestamp}/training_results.json
   └── logs/ (TensorBoard + CSV)
```

---

## ⚙️ Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `training.max_epochs` | 50 | Total training epochs |
| `training.learning_rate` | 5e-5 | Initial learning rate |
| `training.optimizer.name` | AdamW | Optimizer |
| `training.optimizer.weight_decay` | 0.01 | Weight decay |
| `training.scheduler.name` | ReduceLROnPlateau | LR scheduler |
| `training.scheduler.factor` | 0.5 | LR reduction factor |
| `training.scheduler.patience` | 5 | Epochs before LR reduction |
| `data.batch_size` | 8 | Batch size |
| `data.image_size` | 720 | Input resolution |
| `data.num_workers` | 4 | DataLoader workers |

---

## 📊 Metrics Tracked

### During training:
- `train_loss` — logged every 10 steps

### During validation (every epoch):
- `val_mean_iou` — mIoU over **all 7 classes** (incl. background)
- `val_mean_iou_no_bg` — mIoU over **6 semantic classes only** ⭐ (primary metric)

### Model selection:
- Checkpoints saved based on **`val_mean_iou_no_bg`** (higher = better)
- Top 3 checkpoints kept

---

## 💾 Output Structure

After training, your run directory looks like:
```
runs/2026-02-12_14-30-00_720x720/
├── checkpoints/
│   ├── dinov3-mask2former-loveda-epoch=25-val_mean_iou_no_bg=0.35.ckpt
│   ├── dinov3-mask2former-loveda-epoch=40-val_mean_iou_no_bg=0.38.ckpt
│   └── dinov3-mask2former-loveda-epoch=48-val_mean_iou_no_bg=0.40.ckpt
├── training_results.json
└── config.yaml  (saved Hydra config)
```

---

## 📊 Evaluation

### Run evaluation on a checkpoint
```bash
python evaluate_hydra.py \
  checkpoint_path=runs/2026-02-12_14-30-00_720x720/checkpoints/best.ckpt
```

### What it outputs:
- Console: mIoU (all classes), mIoU (semantic only), performance assessment
- File: `evaluation_results.json` with full metrics

---

## 🧊 What's Frozen vs. Trainable

| Component | Trainable? | Why? |
|-----------|-----------|------|
| DINOv3-ViT-L/16 backbone | ❄️ No | Preserves pretrained representations |
| Spatial Prior Module | ✅ Yes | Learns spatial features from image |
| Interaction Blocks | ✅ Yes | Learns to fuse ViT + spatial features |
| Mask2Former head | ✅ Yes | Learns segmentation task |

---

## 🐛 Troubleshooting

### GPU Out of Memory
```bash
# Reduce batch size
python train_hydra.py data.batch_size=2

# Or use gradient accumulation
python train_hydra.py training.accumulate_grad_batches=4 data.batch_size=2
# Effective batch = 2 × 4 = 8
```

### Slow training
```bash
# Increase workers
python train_hydra.py data.num_workers=8
```

### Need HF token
```bash
source env.sh  # Sets HF_TOKEN environment variable
```

### View TensorBoard logs
```bash
tensorboard --logdir logs/
```
