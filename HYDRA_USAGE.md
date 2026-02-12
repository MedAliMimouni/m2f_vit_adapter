# 🚀 Hydra Configuration System Usage Guide

This guide explains how to use the new Hydra-based configuration system for DINOv3+Mask2Former training and evaluation.

## 📁 Configuration Structure

```
conf/
├── config.yaml                    # Main configuration file
├── model/
│   └── dinov3_mask2former.yaml    # Model architecture settings
├── data/
│   └── loveda.yaml                # Dataset and data loading settings
├── training/
│   ├── default.yaml               # Standard training (50 epochs)
│   └── quick_test.yaml            # Quick test (1 epoch)
└── logging/
    └── default.yaml               # Logging and checkpoint settings
```

## 🎯 Key Features

- **🗂️ Organized Configuration**: Modular config files for different components
- **📅 Unique Run Directories**: Each run gets a timestamped directory: `runs/YYYY-MM-DD_HH-MM-SS_736x736/`
- **📋 Config Preservation**: Configuration copied to run directory for reproducibility
- **📊 Dual Metrics**: Both all-classes and semantic-only validation metrics
- **🔧 Easy Overrides**: Change any parameter from command line

## 🚀 Basic Usage

### Training

```bash
# Standard training (50 epochs)
python train_hydra.py

# Quick test (1 epoch)
python train_hydra.py training=quick_test

# Custom parameters
python train_hydra.py training.max_epochs=25 data.batch_size=4

# View configuration before running
python train_hydra.py --cfg job
```

### Evaluation

```bash
# Evaluate a trained model
python evaluate_hydra.py checkpoint_path=runs/2024-01-15_14-30-22_736x736/checkpoints/best.ckpt

# Evaluate with different config
python evaluate_hydra.py checkpoint_path=path/to/checkpoint.ckpt training=quick_test
```

## 📂 Output Directory Structure

Each training run creates a unique directory:

```
runs/2024-01-15_14-30-22_736x736/
├── checkpoints/
│   ├── dinov3-mask2former-loveda-epoch=10-val_mean_iou_no_bg=0.52.ckpt
│   ├── dinov3-mask2former-loveda-epoch=15-val_mean_iou_no_bg=0.54.ckpt
│   └── dinov3-mask2former-loveda-epoch=20-val_mean_iou_no_bg=0.53.ckpt
├── logs/
│   ├── dinov3_mask2former_loveda/        # TensorBoard logs
│   └── dinov3_mask2former_loveda_csv/    # CSV logs
├── config.yaml                          # Complete configuration used
├── training_results.json                # Training summary
└── .hydra/                              # Hydra internal files
```

## 🔧 Configuration Examples

### Modify Training Parameters

```bash
# Change epochs and learning rate
python train_hydra.py training.max_epochs=100 training.learning_rate=1e-4

# Change batch size and workers
python train_hydra.py data.batch_size=16 data.num_workers=8

# Enable data augmentation
python train_hydra.py data.augmentation.enabled=true
```

### Model Configuration

```bash
# Use different interaction layers
python train_hydra.py model.interaction_indexes=[2,5,8,11]

# Change model architecture (if you have other configs)
python train_hydra.py model=dinov2_mask2former
```

### Logging Configuration

```bash
# Change checkpoint monitoring metric
python train_hydra.py logging.checkpoint.monitor=val_mean_iou

# Save more checkpoints
python train_hydra.py logging.checkpoint.save_top_k=5

# Disable TensorBoard
python train_hydra.py logging.loggers.tensorboard.enabled=false
```

## 📊 Metrics Configuration

The system supports dual validation metrics:

- **`val_mean_iou`**: All 7 classes (including background)
- **`val_mean_iou_no_bg`**: 6 semantic classes (excluding background)

```bash
# Monitor all classes for checkpointing
python train_hydra.py training.validation.primary_metric=val_mean_iou

# Disable background metric calculation
python train_hydra.py training.validation.metrics.include_background=false

# Disable semantic-only metric
python train_hydra.py training.validation.metrics.exclude_background=false
```

## 🔍 Useful Commands

### View Current Configuration
```bash
python train_hydra.py --cfg job
python train_hydra.py --cfg job training=quick_test
```

### Dry Run (Check Configuration)
```bash
python train_hydra.py --help
```

### Override Multiple Parameters
```bash
python train_hydra.py \
  training=quick_test \
  data.batch_size=4 \
  training.learning_rate=1e-4 \
  logging.checkpoint.save_top_k=1
```

## 📋 Key Configuration Parameters

### Most Important Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `training.max_epochs` | 50 | Number of training epochs |
| `training.learning_rate` | 5e-5 | Learning rate |
| `data.batch_size` | 8 | Batch size |
| `data.dataset_root` | "../../LoveDA/" | Path to dataset |
| `training.validation.primary_metric` | "val_mean_iou_no_bg" | Metric for model selection |
| `logging.checkpoint.save_top_k` | 3 | Number of best checkpoints to keep |

### Directory and Output Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `output.base_dir` | "runs" | Base directory for outputs |
| `logging.save_config` | true | Save config to run directory |
| `logging.save_results` | true | Save training summary |

## 🎯 Best Practices

1. **Always use meaningful run names**:
   ```bash
   python train_hydra.py run.name="dinov3_loveda_augmented" data.augmentation.enabled=true
   ```

2. **Keep configs for successful runs**:
   - The config.yaml in each run directory can be used to reproduce results

3. **Use quick_test for debugging**:
   ```bash
   python train_hydra.py training=quick_test
   ```

4. **Monitor semantic-only metrics**:
   - Default setup focuses on semantic classes (excluding background)

5. **Organize runs with meaningful names**:
   ```bash
   python train_hydra.py run.description="Testing with augmentation enabled"
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Hydra not found**: Install with `pip install hydra-core`
2. **Config not found**: Make sure you're in the right directory with `conf/` folder
3. **Checkpoint path issues**: Use absolute paths for evaluation
4. **CUDA out of memory**: Reduce batch_size: `data.batch_size=4`

### Debug Commands

```bash
# Check if config loads correctly
python -c "import hydra; from omegaconf import DictConfig; print('Hydra working!')"

# View complete configuration
python train_hydra.py --cfg all

# Check Hydra version
python -c "import hydra; print(hydra.__version__)"
```

## 📈 Migration from Old System

If migrating from `train.py`, the parameters map as follows:

| Old Parameter | New Parameter |
|---------------|---------------|
| `max_epochs=50` | `training.max_epochs=50` |
| `batch_size=8` | `data.batch_size=8` |
| `learning_rate=5e-5` | `training.learning_rate=5e-5` |
| `DATASET_ROOT` | `data.dataset_root` |

## 🎉 Advantages

- **🔄 Reproducibility**: Every run saves its complete configuration
- **🎯 Organization**: Clean separation of concerns
- **📊 Flexibility**: Easy parameter overrides without code changes
- **📁 Management**: Automatic run directory management with timestamps
- **🔍 Transparency**: Always know exactly what configuration was used
- **⚡ Efficiency**: Quick testing with predefined configurations 