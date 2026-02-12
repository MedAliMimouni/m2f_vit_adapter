# 🧠 DINOv3 + ViT-Adapter + Mask2Former

> Semantic segmentation on LoveDA using a frozen DINOv3-ViT-L/16 backbone with a trainable ViT-Adapter and Mask2Former head.

## 🎯 What This Project Does

Combines three powerful components for satellite image segmentation:

| Component | Role | Trainable? |
|-----------|------|------------|
| **DINOv3-ViT-L/16** | Feature extraction backbone (~1B params) | ❄️ Frozen |
| **ViT-Adapter** | Converts single-scale ViT → multi-scale FPN (~50M params) | ✅ Yes |
| **Mask2Former** | Universal segmentation head | ✅ Yes |

**Dataset:** [LoveDA](https://github.com/Junjue-Wang/LoveDA) — 7-class land-use segmentation (building, road, water, barren, forest, agriculture, background)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements_hydra.txt

# 2. Set HuggingFace token
source env.sh

# 3. Train! (720×720, 50 epochs)
python train_hydra.py

# 4. Quick test (1 epoch)
python train_hydra.py training=quick_test

# 5. Evaluate a checkpoint
python evaluate_hydra.py checkpoint_path=runs/<your_run>/checkpoints/best.ckpt
```

---

## 🏗️ Architecture

```
Input Image (720×720)
     │
     ▼
DINOv3-ViT-L/16 (frozen)  ──→  Features at layers [4, 11, 17, 23]
     │
     ▼
ViT-Adapter (trainable)   ──→  Multi-scale FPN: H/4, H/8, H/16, H/32
     │
     ▼
Mask2Former Head           ──→  7-class segmentation map
```

---

## 📁 Project Structure

```
├── train_hydra.py              🏋️ Training script (PyTorch Lightning + Hydra)
├── evaluate_hydra.py           📊 Evaluation script
├── data.py                     📦 LoveDA dataset & dataloaders
├── dinov3_mask2former_integration.py   🧠 Model builder (DINOv3)
├── dinov2_mask2former_integration.py   🧠 Model builder (DINOv2 alt)
├── env.sh                      🔑 Environment secrets (gitignored)
├── models/
│   ├── backbone/dinov3_adapter.py      🔧 ViT-Adapter implementation
│   └── utils/ms_deform_attn.py         🔧 Deformable attention
├── conf/                       ⚙️ Hydra configs
│   ├── config.yaml             Main config (720×720)
│   ├── model/                  Model config
│   ├── data/                   Dataset configs (720, 1024)
│   ├── training/               Training configs (default, quick_test)
│   └── logging/                Logging & checkpoint config
└── docs/                       📖 Documentation
    ├── ARCHITECTURE.md         Model architecture deep-dive
    ├── TRAINING.md             Training guide & usage
    ├── DATA.md                 Dataset & data pipeline
    ├── CONFIGURATION.md        Hydra config reference
    ├── RESULTS.md              Training results & analysis
    └── FILE_MAP.md             Complete file reference
```

---

## 📊 Results So Far

| Model | Epochs | mIoU (semantic) | Best Classes |
|-------|--------|-----------------|--------------|
| DINOv2-ViT-B/14 | 48 | 0.271 | Agriculture (0.50), Building (0.50) |
| DINOv3-ViT-L/16 | early | 0.118 | In progress... |

See [docs/RESULTS.md](docs/RESULTS.md) for full breakdown.

---

## 📖 Documentation

| Doc | What's Inside |
|-----|---------------|
| [Architecture](docs/ARCHITECTURE.md) | 🏗️ Full model architecture, components, parameter counts |
| [Training](docs/TRAINING.md) | 🏋️ How to train, hyperparameters, troubleshooting |
| [Data](docs/DATA.md) | 📦 LoveDA dataset, classes, preprocessing pipeline |
| [Configuration](docs/CONFIGURATION.md) | ⚙️ All Hydra config options + CLI overrides |
| [Results](docs/RESULTS.md) | 📊 Training metrics, per-class analysis, improvements |
| [File Map](docs/FILE_MAP.md) | 🗂️ Every file and what it does |

---

## 🛠️ Common Commands

```bash
# Train with defaults
python train_hydra.py

# Quick test (1 epoch)
python train_hydra.py training=quick_test

# High-resolution (1024×1024)
python train_hydra.py --config-name=config_1024

# Custom params
python train_hydra.py training.max_epochs=100 training.learning_rate=1e-4 data.batch_size=4

# View TensorBoard
tensorboard --logdir logs/

# View resolved config
python train_hydra.py --cfg job
```
