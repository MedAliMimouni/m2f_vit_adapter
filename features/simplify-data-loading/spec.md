# Feature: Simplify Data Loading

**Status:** APPROVED
**Created:** 2026-02-06

## Overview

Refactor the data loading pipeline from a PyTorch Lightning `LightningDataModule` to a bare-bones, standard PyTorch implementation. The goal is maximum readability and minimal boilerplate while preserving the exact same data processing behavior.

## Motivation

The current `LoveDADataModule` wraps simple data loading logic in Lightning-specific abstractions (`setup()`, `train_dataloader()`, etc.) that obscure what's actually happening. A standard PyTorch `Dataset` + manual `DataLoader` instantiation makes the pipeline transparent and removes the `pytorch_lightning` dependency from data loading.

## User Stories

### US-1: Replace LightningDataModule with standard PyTorch Dataset and factory function

**As a** developer working on this project
**I want** the data loading code to use only standard PyTorch (`torch.utils.data.Dataset`, `torch.utils.data.DataLoader`)
**So that** I can see exactly how data flows without Lightning abstractions

**Acceptance Criteria:**
- `data.py` contains a `LoveDADataset` class inheriting from `torch.utils.data.Dataset`
- `data.py` contains a `create_dataloaders()` factory function that returns train, val, and test `DataLoader` objects
- `data.py` retains the custom `collate_fn` for variable-length Mask2Former mask batching
- The `LoveDADataModule` class and all `pytorch_lightning` imports are removed from `data.py`
- The HuggingFace `AutoImageProcessor` (Mask2Former processor) is still used for preprocessing
- The `LoveDADataset.__getitem__` returns the same dict format: `{"pixel_values", "mask_labels", "class_labels"}`
- No visualization utilities (`visualize_batch`, `_colorize_mask`, `CLASS_NAMES`, `CLASS_COLORS`) in `data.py`
- No `main_example()` function or `if __name__ == '__main__'` block

### US-2: Delete dataset.py

**As a** developer
**I want** the redundant `dataset.py` file removed
**So that** there is a single, clear source of truth for data loading

**Acceptance Criteria:**
- `dataset.py` is deleted from the project
- No other files import from `dataset.py` (verify no breakage)

### US-3: Delete augmentations.py

**As a** developer
**I want** the unused `augmentations.py` file removed
**So that** the project only contains code that is actually in use

**Acceptance Criteria:**
- `augmentations.py` is deleted from the project
- No other files import from `augmentations.py` (verify no breakage)

### US-4: Delete evaluate_model.py

**As a** developer
**I want** the redundant `evaluate_model.py` removed
**So that** there is a single evaluation script (`evaluate_hydra.py`) and no broken imports after the refactor

**Acceptance Criteria:**
- `evaluate_model.py` is deleted from the project
- No other files import from `evaluate_model.py` (verify no breakage)

### US-5: Update train.py to use new data loading

**As a** developer
**I want** `train.py` to use the new `create_dataloaders()` function instead of `LoveDADataModule`
**So that** the training script works with the simplified data loading

**Acceptance Criteria:**
- `train.py` imports `create_dataloaders` (and `LoveDADataset` if needed) from `data` instead of `LoveDADataModule`
- `train.py` calls `create_dataloaders()` to get train/val/test DataLoaders directly
- The DataLoaders are passed to the training loop in whatever way is appropriate (this may require adjusting how Lightning Trainer receives data, or replacing the Trainer with a manual loop — depending on whether Lightning is still used for training)
- The same batch_size, num_workers, and processor configuration is preserved

### US-6: Update train_hydra.py to use new data loading

**As a** developer
**I want** `train_hydra.py` to use the new `create_dataloaders()` function instead of `LoveDADataModule`
**So that** the Hydra-based training script works with the simplified data loading

**Acceptance Criteria:**
- `train_hydra.py` imports `create_dataloaders` from `data` instead of `LoveDADataModule`
- `train_hydra.py` calls `create_dataloaders()` with config-driven parameters
- The same batch_size, num_workers, image_size, and processor configuration is preserved

## Functional Requirements

### FR-1: LoveDADataset class

The `LoveDADataset` class must:
- Inherit from `torch.utils.data.Dataset`
- Accept `split_dir` (path to Train/Val/Test directory) and `processor` (HuggingFace AutoImageProcessor) as required parameters
- Accept an optional `transform` parameter
- Scan `Rural/` and `Urban/` subdirectories for PNG image/mask pairs
- Load images as RGB, masks as grayscale
- Process through the HuggingFace processor
- Return a dict with keys: `pixel_values`, `mask_labels`, `class_labels`
- Implement `__len__` and `__getitem__`

### FR-2: collate_fn function

The standalone `collate_fn` must:
- Stack `pixel_values` into a single tensor
- Keep `mask_labels` and `class_labels` as lists (due to variable lengths per sample)
- Return a dict with keys: `pixel_values`, `mask_labels`, `class_labels`

### FR-3: create_dataloaders factory function

The `create_dataloaders()` function must:
- Accept parameters: `data_dir`, `processor`, `batch_size`, `num_workers`
- Create `LoveDADataset` instances for Train, Val, and Test splits
- Return three `DataLoader` objects: train (shuffle=True), val (shuffle=False), test (shuffle=False)
- All DataLoaders use the custom `collate_fn`
- All DataLoaders use `pin_memory=True` (hardcoded, for GPU transfer performance)

### FR-4: Training script compatibility

Both `train.py` and `train_hydra.py` must:
- Replace `LoveDADataModule` usage with `create_dataloaders()` calls
- Pass the resulting DataLoaders to the Lightning Trainer via: `trainer.fit(model, train_dataloaders=train_loader, val_dataloaders=val_loader)`
- Preserve all existing configuration values (batch_size, num_workers, processor settings)

## Data Format (unchanged)

- **Input:** PNG images (RGB) and PNG masks (grayscale) from LoveDA dataset
- **Dataset structure:**
  ```
  LoveDA/
  ├── Train/
  │   ├── Urban/
  │   │   ├── images_png/
  │   │   └── masks_png/
  │   └── Rural/
  │       ├── images_png/
  │       └── masks_png/
  ├── Val/
  └── Test/
  ```
- **Output per sample:** `{"pixel_values": Tensor, "mask_labels": Tensor, "class_labels": Tensor}`
- **Output per batch:** `{"pixel_values": stacked Tensor, "mask_labels": list of Tensors, "class_labels": list of Tensors}`

## Out of Scope

- Changing the model architecture or training loop logic
- Adding data augmentation (currently disabled and augmentations.py will be deleted)
- Changing the HuggingFace processor configuration
- Modifying config YAML files
- Performance optimization of data loading
- Adding new features to the Dataset class (domain filtering, class weights, etc.)

## Edge Cases

- **Missing Test split:** The Test split may not have masks. `create_dataloaders()` should handle this gracefully (skip test DataLoader if Test directory doesn't exist or has no masks).
- **Empty directories:** If a Rural or Urban subdirectory is missing, skip it silently (current behavior, preserve it).
