# Implementation Plan: Simplify Data Loading

**Status:** APPROVED
**Spec:** [spec.md](./spec.md)
**Created:** 2026-02-06
**Approved:** 2026-02-06

## Overview

Replace the PyTorch Lightning `LoveDADataModule` in `data.py` with a plain PyTorch `Dataset` + a `create_dataloaders()` factory function. Delete three redundant files (`dataset.py`, `augmentations.py`, `evaluate_model.py`). Update both training scripts to pass DataLoaders directly to the Lightning Trainer instead of a DataModule.

The approach is conservative: keep `LoveDADataset` and `collate_fn` nearly identical to their current implementations, only removing the Lightning wrapper and visualization code. The training scripts get a minimal 3-line change (import + create loaders + pass to trainer).

---

## Phases

### Phase 1: Rewrite data.py

**Objective:** Replace data.py contents with the simplified Dataset + factory function, removing all Lightning and visualization code.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Rewrite `data.py`: keep `collate_fn` (lines 14-28) unchanged, keep `LoveDADataset` class (lines 30-99) unchanged, remove `LoveDADataModule` class (lines 102-229), remove `main_example()` (lines 232-270), remove `pytorch_lightning` / `matplotlib` / `numpy` imports, add `create_dataloaders()` factory function | `data.py` | modify |

**Details for `create_dataloaders()`:**
```python
def create_dataloaders(data_dir, processor, batch_size=4, num_workers=4):
    train_dir = os.path.join(data_dir, "Train")
    val_dir = os.path.join(data_dir, "Val")
    test_dir = os.path.join(data_dir, "Test")

    train_dataset = LoveDADataset(train_dir, processor)
    val_dataset = LoveDADataset(val_dir, processor)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, collate_fn=collate_fn, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False,
                            num_workers=num_workers, collate_fn=collate_fn, pin_memory=True)

    # Test split may not have masks — create loader only if directory exists and has samples
    test_loader = None
    if os.path.isdir(test_dir):
        test_dataset = LoveDADataset(test_dir, processor)
        if len(test_dataset) > 0:
            test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False,
                                     num_workers=num_workers, collate_fn=collate_fn, pin_memory=True)

    return train_loader, val_loader, test_loader
```

**Final `data.py` structure (top to bottom):**
1. Imports: `os`, `PIL.Image`, `torch`, `torch.utils.data.Dataset`, `torch.utils.data.DataLoader`
2. `collate_fn()` — unchanged from current
3. `LoveDADataset(Dataset)` — unchanged from current (lines 30-99)
4. `create_dataloaders()` — new factory function

**Verification:** `python -c "from data import LoveDADataset, collate_fn, create_dataloaders"` succeeds. `python -c "import data; print(dir(data))"` shows no Lightning references.

---

### Phase 2: Delete redundant files

**Objective:** Remove `dataset.py`, `augmentations.py`, and `evaluate_model.py`. All three have been verified to have zero imports from other project files.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Delete `dataset.py` | `dataset.py` | delete |
| 2 | Delete `augmentations.py` | `augmentations.py` | delete |
| 3 | Delete `evaluate_model.py` | `evaluate_model.py` | delete |

**Verification:** `python -c "from data import LoveDADataset, collate_fn, create_dataloaders"` still succeeds. `python -c "from evaluate_hydra import main"` still succeeds (it imports `LoveDADataset` and `collate_fn` from `data`, which still exist).

---

### Phase 3: Update training scripts

**Objective:** Replace `LoveDADataModule` usage in both training scripts with `create_dataloaders()`.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | In `train.py` line 260: change `from data import LoveDADataModule` to `from data import create_dataloaders` | `train.py` | modify |
| 2 | In `train.py` lines 274-279: replace `data_module = LoveDADataModule(...)` with `train_loader, val_loader, _ = create_dataloaders(data_dir=DATASET_ROOT, processor=processor, batch_size=8, num_workers=4)` | `train.py` | modify |
| 3 | In `train.py` line 320: change `trainer.fit(model=model_module, datamodule=data_module)` to `trainer.fit(model=model_module, train_dataloaders=train_loader, val_dataloaders=val_loader)` | `train.py` | modify |
| 4 | In `train_hydra.py` line 273: change `from data import LoveDADataModule` to `from data import create_dataloaders` | `train_hydra.py` | modify |
| 5 | In `train_hydra.py` lines 283-288: replace `data_module = LoveDADataModule(...)` with `train_loader, val_loader, _ = create_dataloaders(data_dir=cfg.data.dataset_root, processor=processor, batch_size=cfg.data.batch_size, num_workers=cfg.data.num_workers)` | `train_hydra.py` | modify |
| 6 | In `train_hydra.py` line 332: change `trainer.fit(model=model_module, datamodule=data_module)` to `trainer.fit(model=model_module, train_dataloaders=train_loader, val_dataloaders=val_loader)` | `train_hydra.py` | modify |

**Verification:** `python -c "import train"` and `python -c "import train_hydra"` succeed without import errors. Grep the project for `LoveDADataModule` — should return zero results in .py files.

---

## Testing Strategy

This is a refactor with no new logic. Testing focuses on verifying nothing broke.

### Smoke Tests (manual)
- `python -c "from data import LoveDADataset, collate_fn, create_dataloaders"` — imports work
- `python -c "import train"` — no import errors
- `python -c "import train_hydra"` — no import errors
- `python -c "from evaluate_hydra import main"` — no import errors

### Grep Verification
- `grep -r "LoveDADataModule" *.py` returns no results
- `grep -r "from dataset " *.py` returns no results
- `grep -r "from augmentation" *.py` returns no results
- `grep -r "from evaluate_model" *.py` returns no results

### Functional Test (if dataset is available)
- Run `train.py` for 1 epoch to verify end-to-end data flow is unchanged

---

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `LoveDADataset` warning on missing Test masks stops `create_dataloaders()` | Low | Low | The existing class already prints a WARNING and returns 0 length; the factory checks `len() > 0` before creating loader |
| Lightning Trainer rejects DataLoaders passed directly (version incompatibility) | Low | High | `train_dataloaders` parameter has been supported since Lightning 1.x; current codebase already uses a recent Lightning version |

---

## Breaking Changes

- `data.py` no longer exports `LoveDADataModule`. Any external code importing it will break. Within this project, only `train.py`, `train_hydra.py`, and `evaluate_model.py` (deleted) used it.
- `evaluate_model.py` is deleted. If anyone has scripts that invoke it, they should use `evaluate_hydra.py` instead.
- `dataset.py` and `augmentations.py` are deleted. No project files imported them.

---

## Migration Steps

No data or schema migrations required. This is a pure code refactor.
