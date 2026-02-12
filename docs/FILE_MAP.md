# 🗂️ File Map — Quick Reference

> Every file in this project and what it does. Use this to orient yourself fast.

## 📁 Project Root

| File | Purpose |
|------|---------|
| `train_hydra.py` | 🏋️ **Main training script** — PyTorch Lightning + Hydra. Trains the model on LoveDA |
| `evaluate_hydra.py` | 📊 **Evaluation script** — Loads checkpoint, runs validation, outputs metrics |
| `data.py` | 📦 **Dataset & DataLoaders** — `LoveDADataset` class + `create_dataloaders()` factory |
| `dinov3_mask2former_integration.py` | 🧠 **DINOv3 model builder** — Creates integrated DINOv3 + Adapter + Mask2Former model |
| `dinov2_mask2former_integration.py` | 🧠 **DINOv2 model builder** — Alternative using DINOv2-ViT-B/14 backbone |
| `env.sh` | 🔑 **Environment secrets** — HuggingFace token (gitignored) |
| `requirements_hydra.txt` | 📋 **Dependencies** — All pip packages needed |
| `training_results.json` | 📈 **Training output** — Best metrics from DINOv3 training |
| `__init__.py` | 📦 Package init (empty) |

## 📁 `models/` — Model Architecture

| File | Purpose |
|------|---------|
| `models/backbone/dinov3_adapter.py` | 🔧 **Core adapter** — `DINOv3_Adapter` class: converts single-scale ViT → multi-scale FPN |
| `models/utils/ms_deform_attn.py` | 🔧 **Deformable attention** — `MSDeformAttn` module for efficient multi-scale attention |
| `models/utils/ops/` | ⚡ **CUDA ops** — Optional compiled C++/CUDA kernels for faster deformable attention |

## 📁 `conf/` — Hydra Configuration

| File | Purpose |
|------|---------|
| `conf/config.yaml` | ⚙️ **Main config** — Composes all sub-configs (720×720 default) |
| `conf/config_1024.yaml` | ⚙️ **High-res config** — Same but with 1024×1024 images |
| `conf/model/dinov3_mask2former.yaml` | ⚙️ **Model config** — Backbone name, interaction indexes, num_classes |
| `conf/data/loveda.yaml` | ⚙️ **Data config (720)** — Dataset paths, batch size, class names/colors |
| `conf/data/loveda_1024.yaml` | ⚙️ **Data config (1024)** — Same but 1024×1024 |
| `conf/training/default.yaml` | ⚙️ **Training config** — Epochs, LR, optimizer, scheduler |
| `conf/training/quick_test.yaml` | ⚙️ **Quick test config** — 1 epoch for debugging |
| `conf/logging/default.yaml` | ⚙️ **Logging config** — TensorBoard, CSV, checkpointing |

## 📁 `evaluation_results/` — Past Evaluation Outputs

| File | Purpose |
|------|---------|
| `evaluation_results/evaluation_summary.txt` | 📊 Overall metrics (mIoU, accuracy, F1) from DINOv2 eval |
| `evaluation_results/classification_report.txt` | 📊 Per-class precision, recall, F1, IoU |
| `evaluation_results/confusion_matrix.png` | 📊 Confusion matrix visualization |
| `evaluation_results/prediction_samples.png` | 📊 Sample prediction visualizations |

## 📁 `logs/` — Training Logs

| Directory | Purpose |
|-----------|---------|
| `logs/dinov3_mask2former_loveda/` | 📈 TensorBoard logs (DINOv3 runs) |
| `logs/dinov3_mask2former_loveda_csv/` | 📈 CSV metric logs (DINOv3 runs) |
| `logs/dinov2_mask2former_loveda/` | 📈 TensorBoard logs (DINOv2 runs) |

## 📁 `docs/` — Documentation

| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE.md` | 🏗️ Model architecture deep-dive |
| `docs/TRAINING.md` | 🏋️ Training pipeline & usage guide |
| `docs/DATA.md` | 📦 Dataset & data loading docs |
| `docs/CONFIGURATION.md` | ⚙️ Hydra config reference |
| `docs/RESULTS.md` | 📊 Training/evaluation results & analysis |
| `docs/FILE_MAP.md` | 🗂️ This file |
