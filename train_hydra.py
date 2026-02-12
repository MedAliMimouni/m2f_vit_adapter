import torch
import pytorch_lightning as pl
from transformers import AutoImageProcessor, Mask2FormerConfig
from torchmetrics.classification import JaccardIndex
import hydra
from omegaconf import DictConfig, OmegaConf
import os
import shutil
from datetime import datetime
from pathlib import Path

# Import the model creation function from the new DINOv3 integration script
from dinov3_mask2former_integration import create_dinov3_mask2former

class SegmentationLightningModule(pl.LightningModule):
    """
    PyTorch Lightning module for fine-tuning the DINOv3+Mask2Former model.
    """
    def __init__(self, cfg: DictConfig):
        """
        Args:
            cfg: Hydra configuration object
        """
        super().__init__()
        self.cfg = cfg
        self.learning_rate = cfg.training.learning_rate
        self.num_classes = cfg.model.num_classes
        self.logged_shapes = False  # Flag to log shapes only once

        # Setup processor
        self.processor = AutoImageProcessor.from_pretrained(
            cfg.model.processor.name,
            do_reduce_labels=cfg.model.processor.do_reduce_labels,
            ignore_index=cfg.model.processor.ignore_index,
            size={"height": cfg.data.image_size, "width": cfg.data.image_size}
        )

        # 1. Instantiate the Model
        model_kwargs = {
            "dinov3_model_name": cfg.model.dinov3_model_name,
            "interaction_indexes": cfg.model.interaction_indexes,
        }
        self.model, _, _ = create_dinov3_mask2former(
            num_classes=self.num_classes, **model_kwargs
        )

        # 2. Instantiate the Evaluation Metrics (mIoU)
        self.val_mean_iou = JaccardIndex(
            task="multiclass", 
            num_classes=self.num_classes, 
            ignore_index=255
        )
        
        # Additional validation metric that excludes background (class 0)
        if cfg.training.validation.metrics.exclude_background:
            self.val_mean_iou_no_bg = JaccardIndex(
                task="multiclass", 
                num_classes=self.num_classes - 1,
                ignore_index=255
            )
        
        # Test metrics (separate instance for testing)
        self.test_mean_iou = JaccardIndex(
            task="multiclass", 
            num_classes=self.num_classes, 
            ignore_index=255
        )

    def forward(self, pixel_values, mask_labels=None, class_labels=None):
        """Forward pass through the model."""
        return self.model(
            pixel_values=pixel_values,
            mask_labels=mask_labels,
            class_labels=class_labels
        )

    def training_step(self, batch, batch_idx):
        """
        Defines one step of the training loop.
        """
        # Log image shapes on first batch of first epoch
        if not self.logged_shapes:
            pixel_values_shape = batch["pixel_values"].shape
            print(f"📐 Training batch shapes:")
            print(f"  Pixel values: {pixel_values_shape}")
            print(f"  Batch size: {pixel_values_shape[0]}")
            print(f"  Image size: {pixel_values_shape[2]}×{pixel_values_shape[3]}")
            
            # Calculate patch information for DINOv3
            patch_size = 16  # DINOv3 patch size
            h, w = pixel_values_shape[2], pixel_values_shape[3]
            patches_h, patches_w = h // patch_size, w // patch_size
            total_patches = patches_h * patches_w
            print(f"  Patches: {patches_h}×{patches_w} = {total_patches}")
            print(f"  Total tokens: {total_patches} + 1 CLS + 4 registers = {total_patches + 5}")
            print(f"  Resolution level: HIGH ({patches_h}×{patches_w} patches)")
            
            self.logged_shapes = True
        
        outputs = self.forward(
            pixel_values=batch["pixel_values"],
            mask_labels=batch["mask_labels"],
            class_labels=batch["class_labels"],
        )
        
        loss = outputs.loss
        
        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True, batch_size=batch["pixel_values"].shape[0])
        return loss

    def validation_step(self, batch, batch_idx):
        """
        Defines one step of the validation loop.
        """
        outputs = self.model(pixel_values=batch["pixel_values"])
        
        # Post-process the raw outputs to get the final segmentation map.
        original_sizes = [tuple(img.shape[-2:]) for img in batch["pixel_values"]]
        predicted_maps = self.processor.post_process_semantic_segmentation(
            outputs, target_sizes=original_sizes
        )
        
        # Reconstruct the ground truth mask from the processor's format.
        ground_truth_maps = []
        for i in range(len(batch["pixel_values"])):
            gt_map = torch.full_like(predicted_maps[i], 255)
            for mask, class_id in zip(batch["mask_labels"][i], batch["class_labels"][i]):
                gt_map[mask.bool()] = class_id.item()
            ground_truth_maps.append(gt_map)

        # Ensure predictions are valid (clamp to valid class range)
        pred_maps_clamped = []
        for pred_map in predicted_maps:
            pred_clamped = torch.clamp(pred_map, 0, self.num_classes - 1)
            pred_maps_clamped.append(pred_clamped)
        
        preds_tensor = torch.stack(pred_maps_clamped)
        gt_tensor = torch.stack(ground_truth_maps)
        
        # Ensure tensors are on the same device and have the correct dtype
        preds_tensor = preds_tensor.to(self.device).long()
        gt_tensor = gt_tensor.to(self.device).long()
        
        # Update standard validation metric (includes background)
        if self.cfg.training.validation.metrics.include_background:
            self.val_mean_iou.update(preds_tensor, gt_tensor)
        
        # Prepare tensors for no-background metric
        if self.cfg.training.validation.metrics.exclude_background:
            preds_no_bg = preds_tensor.clone()
            gt_no_bg = gt_tensor.clone()
            
            for original_class in range(self.num_classes):
                if original_class == 0:  # background -> ignore
                    preds_no_bg[preds_tensor == original_class] = 255
                    gt_no_bg[gt_tensor == original_class] = 255
                else:  # classes 1-6 -> 0-5
                    preds_no_bg[preds_tensor == original_class] = original_class - 1
                    gt_no_bg[gt_tensor == original_class] = original_class - 1
            
            # Update no-background validation metric (semantic classes only)
            self.val_mean_iou_no_bg.update(preds_no_bg, gt_no_bg)

    def on_validation_epoch_end(self):
        """
        Called at the end of the validation epoch to compute and log metrics.
        """
        metrics = {}
        current_epoch = self.current_epoch
        
        # Compute metrics based on configuration
        if self.cfg.training.validation.metrics.include_background:
            miou = self.val_mean_iou.compute()
            metrics["val_mean_iou"] = miou
            self.log("val_mean_iou", miou, prog_bar=True, logger=True, sync_dist=True)
        
        if self.cfg.training.validation.metrics.exclude_background:
            miou_no_bg = self.val_mean_iou_no_bg.compute()
            metrics["val_mean_iou_no_bg"] = miou_no_bg  
            self.log("val_mean_iou_no_bg", miou_no_bg, prog_bar=True, logger=True, sync_dist=True)
        
        # Print progress info
        if len(metrics) == 2:
            print(f"🎯 Epoch {current_epoch}: val_mean_iou = {metrics['val_mean_iou']:.4f} | val_mean_iou_no_bg = {metrics['val_mean_iou_no_bg']:.4f}")
            print(f"   📊 All classes: {metrics['val_mean_iou']:.1%} | Semantic only: {metrics['val_mean_iou_no_bg']:.1%}")
        elif "val_mean_iou_no_bg" in metrics:
            print(f"🎯 Epoch {current_epoch}: val_mean_iou_no_bg = {metrics['val_mean_iou_no_bg']:.4f} ({metrics['val_mean_iou_no_bg']:.1%})")
        elif "val_mean_iou" in metrics:
            print(f"🎯 Epoch {current_epoch}: val_mean_iou = {metrics['val_mean_iou']:.4f} ({metrics['val_mean_iou']:.1%})")
        
        # Reset metrics
        if self.cfg.training.validation.metrics.include_background:
            self.val_mean_iou.reset()
        if self.cfg.training.validation.metrics.exclude_background:
            self.val_mean_iou_no_bg.reset()

    def configure_optimizers(self):
        """
        Configures the optimizer and learning rate scheduler.
        """
        trainable_params = [
            p for n, p in self.model.named_parameters() 
            if "dinov3_backbone" not in n and p.requires_grad
        ]
        
        print(f"Found {len(trainable_params)} trainable parameters.")
        
        # Configure optimizer based on config
        if self.cfg.training.optimizer.name == "AdamW":
            optimizer = torch.optim.AdamW(
                trainable_params, 
                lr=self.learning_rate,
                weight_decay=self.cfg.training.optimizer.weight_decay
            )
        
        # Configure scheduler based on config
        if self.cfg.training.scheduler.name == "ReduceLROnPlateau":
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, 
                mode=self.cfg.training.scheduler.mode,
                factor=self.cfg.training.scheduler.factor,
                patience=self.cfg.training.scheduler.patience
            )
            
            return {
                "optimizer": optimizer,
                "lr_scheduler": {
                    "scheduler": scheduler,
                    "monitor": self.cfg.training.scheduler.monitor,
                },
            }
        
        return optimizer


def setup_run_directory(cfg: DictConfig) -> Path:
    """Setup the run directory and copy config."""
    # Hydra automatically sets the working directory to the output directory
    run_dir = Path.cwd()
    
    # Create subdirectories
    (run_dir / "checkpoints").mkdir(exist_ok=True)
    (run_dir / "logs").mkdir(exist_ok=True)
    
    # Save the resolved config
    if cfg.logging.save_config:
        config_path = run_dir / "config.yaml"
        with open(config_path, 'w') as f:
            OmegaConf.save(config=cfg, f=f)
        print(f"📁 Config saved to: {config_path}")
    
    return run_dir


@hydra.main(version_base="1.3", config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """Main training function with Hydra configuration."""
    
    print("🚀 Starting DINOv3+Mask2Former training with Hydra")
    print("=" * 60)
    print(f"📁 Run directory: {os.getcwd()}")
    print(f"🎯 Run name: {cfg.run.name}")
    print(f"📝 Description: {cfg.run.description}")
    print("=" * 60)
    
    # Set matmul precision
    torch.set_float32_matmul_precision(cfg.training.precision)
    
    # Setup run directory
    run_dir = setup_run_directory(cfg)
    
    # Import data loading
    from data import create_dataloaders

    # Setup data from config
    processor = AutoImageProcessor.from_pretrained(
        cfg.model.processor.name,
        do_reduce_labels=cfg.model.processor.do_reduce_labels,
        ignore_index=cfg.model.processor.ignore_index,
        size={"height": cfg.data.image_size, "width": cfg.data.image_size}
    )

    train_loader, val_loader, _ = create_dataloaders(
        data_dir=cfg.data.dataset_root,
        processor=processor,
        batch_size=cfg.data.batch_size,
        num_workers=cfg.data.num_workers
    )
    
    # Setup Lightning module
    model_module = SegmentationLightningModule(cfg)
    
    # Setup callbacks
    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        monitor=cfg.logging.checkpoint.monitor,
        dirpath="checkpoints",  # Relative to run directory
        filename=cfg.logging.checkpoint.filename,
        save_top_k=cfg.logging.checkpoint.save_top_k,
        mode=cfg.logging.checkpoint.mode,
        auto_insert_metric_name=cfg.logging.checkpoint.auto_insert_metric_name,
    )
    
    # Setup loggers
    loggers = []
    if cfg.logging.loggers.tensorboard.enabled:
        loggers.append(
            pl.loggers.TensorBoardLogger(
                "logs", 
                name=cfg.logging.loggers.tensorboard.name
            )
        )
    if cfg.logging.loggers.csv.enabled:
        loggers.append(
            pl.loggers.CSVLogger(
                "logs", 
                name=cfg.logging.loggers.csv.name
            )
        )
    
    # Setup trainer
    trainer = pl.Trainer(
        max_epochs=cfg.training.max_epochs,
        accelerator="auto",
        devices="auto",
        callbacks=[checkpoint_callback],
        logger=loggers,
        log_every_n_steps=cfg.logging.log_every_n_steps,
    )
    
    # Start training
    print("🚀 Starting training...")
    trainer.fit(model=model_module, train_dataloaders=train_loader, val_dataloaders=val_loader)
    
    # Training Summary
    print("\n" + "="*60)
    print("🏆 TRAINING COMPLETE!")
    print("="*60)
    
    if checkpoint_callback.best_model_path:
        print(f"📁 Best checkpoint saved: {checkpoint_callback.best_model_path}")
        print(f"🎯 Best validation mIoU ({cfg.training.validation.primary_metric}): {checkpoint_callback.best_model_score:.4f} ({checkpoint_callback.best_model_score:.1%})")
        
        # Performance assessment
        if checkpoint_callback.best_model_score > 0.5:
            performance = "🏆 Outstanding"
        elif checkpoint_callback.best_model_score > 0.4:
            performance = "🏆 Excellent" 
        elif checkpoint_callback.best_model_score > 0.3:
            performance = "✅ Strong"
        elif checkpoint_callback.best_model_score > 0.2:
            performance = "📈 Good"
        else:
            performance = "🔄 Developing"
        
        print(f"📊 Performance Level: {performance}")
        
        # Save training summary
        if cfg.logging.save_results:
            import json
            results_summary = {
                "model": cfg.model.name,
                "dataset": cfg.data.name,
                "best_val_miou_metric": cfg.training.validation.primary_metric,
                                  "best_val_miou_score": float(checkpoint_callback.best_model_score),
                  "num_classes": cfg.model.num_classes,
                  "image_size": f"{cfg.data.image_size}x{cfg.data.image_size}",
                  "patches_per_side": cfg.data.image_size // 16,
                  "total_patches": (cfg.data.image_size // 16) ** 2,
                "batch_size": cfg.data.batch_size,
                "interaction_indexes": cfg.model.interaction_indexes,
                "config_path": str(run_dir / "config.yaml"),
                "note": "mIoU calculated based on configured metrics"
            }
            
            results_path = run_dir / cfg.logging.results_filename
            with open(results_path, "w") as f:
                json.dump(results_summary, f, indent=2)
            print(f"📄 Training summary saved to: {results_path}")
        
    else:
        print("⚠️  No best checkpoint found.")
        print("💡 This might happen if training was interrupted early.")
    
    print(f"\n✅ Training complete!")
    print(f"📊 Check logs/ for detailed metrics") 
    print(f"💡 Note: Test set evaluation skipped (no ground truth masks available)")
    print(f"🚀 Use evaluation script with same config for comprehensive evaluation")


if __name__ == '__main__':
    main() 