# ⚙️ Configuration Reference

> Hydra-based modular configuration system

## 📁 Config Structure

```
conf/
├── config.yaml                  ← Main entry point (720×720)
├── config_1024.yaml             ← Alternative entry point (1024×1024)
├── model/
│   └── dinov3_mask2former.yaml  ← Model architecture
├── data/
│   ├── loveda.yaml              ← Dataset (720×720)
│   └── loveda_1024.yaml         ← Dataset (1024×1024)
├── training/
│   ├── default.yaml             ← Training params (50 epochs)
│   └── quick_test.yaml          ← Quick test (1 epoch)
└── logging/
    └── default.yaml             ← Logging & checkpoints
```

---

## 🔧 Config Files — Full Reference

### `config.yaml` (Main)
```yaml
defaults:
  - model: dinov3_mask2former
  - data: loveda              # 720×720
  - training: default         # 50 epochs
  - logging: default
```

### `model/dinov3_mask2former.yaml`
```yaml
model:
  name: "DINOv3-ViT-L/16 + Mask2Former"
  backbone: "facebook/dinov3-vitl16-pretrain-sat493m"
  interaction_indexes: [4, 11, 17, 23]   # ViT-L layers to extract from
  num_classes: 7                          # LoveDA classes
  processor:
    name: "facebook/mask2former-swin-base-coco-panoptic"
    do_reduce_labels: true
    ignore_index: 0
```

### `data/loveda.yaml`
```yaml
data:
  name: "LoveDA"
  dataset_root: "/mnt/biontech/temp_mimouni/LoveDA/"
  image_size: 720
  batch_size: 8
  num_workers: 4
  pin_memory: true
  class_names: [background, building, road, water, barren, forest, agriculture]
```

### `training/default.yaml`
```yaml
training:
  max_epochs: 50
  learning_rate: 5e-5
  optimizer:
    name: "AdamW"
    weight_decay: 0.01
  scheduler:
    name: "ReduceLROnPlateau"
    mode: "max"
    factor: 0.5
    patience: 5
    monitor: "val_mean_iou_no_bg"
  precision: "medium"
```

### `logging/default.yaml`
```yaml
logging:
  checkpoint:
    monitor: "val_mean_iou_no_bg"
    mode: "max"
    save_top_k: 3
  loggers:
    tensorboard: { enabled: true }
    csv: { enabled: true }
  log_every_n_steps: 10
```

---

## 🎛️ CLI Overrides

Hydra lets you override **any** config value from the command line:

### Common overrides
```bash
# Change epochs
python train_hydra.py training.max_epochs=100

# Change learning rate
python train_hydra.py training.learning_rate=1e-4

# Change batch size
python train_hydra.py data.batch_size=4

# Change image size
python train_hydra.py data.image_size=512

# Multiple overrides
python train_hydra.py training.max_epochs=100 training.learning_rate=1e-4 data.batch_size=4
```

### Switch config groups
```bash
# Use quick test training config
python train_hydra.py training=quick_test

# Use 1024×1024 data config
python train_hydra.py data=loveda_1024

# Use alternate main config
python train_hydra.py --config-name=config_1024
```

### Inspect full resolved config
```bash
python train_hydra.py --cfg job        # Print resolved config
python train_hydra.py --cfg hydra      # Print Hydra internal config
python train_hydra.py --info config    # Print config search path
```

---

## 🧩 Adding New Configs

### New dataset config
Create `conf/data/my_dataset.yaml`:
```yaml
data:
  name: "MyDataset"
  dataset_root: "/path/to/data/"
  image_size: 512
  batch_size: 4
  num_workers: 4
  pin_memory: true
  class_names: [bg, class1, class2]
```
Use it: `python train_hydra.py data=my_dataset`

### New training config
Create `conf/training/long_run.yaml`:
```yaml
training:
  max_epochs: 200
  learning_rate: 1e-5
  # ... rest of params
```
Use it: `python train_hydra.py training=long_run`
