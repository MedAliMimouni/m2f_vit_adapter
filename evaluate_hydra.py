import torch
import numpy as np
from torch.utils.data import DataLoader
from transformers import AutoImageProcessor
import hydra
from omegaconf import DictConfig, OmegaConf
import os
from pathlib import Path
from tqdm import tqdm
import json

from train_hydra import SegmentationLightningModule
from data import LoveDADataset, collate_fn
from torchmetrics.classification import JaccardIndex


@hydra.main(version_base="1.3", config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """
    Comprehensive model evaluation using Hydra configuration.
    
    Usage:
        python evaluate_hydra.py checkpoint_path=/path/to/checkpoint.ckpt
        python evaluate_hydra.py checkpoint_path=/path/to/checkpoint.ckpt training=quick_test
    """
    
    # Check if checkpoint path is provided
    checkpoint_path = getattr(cfg, 'checkpoint_path', None)
    if checkpoint_path is None:
        print("❌ Error: Please provide checkpoint_path")
        print("Usage: python evaluate_hydra.py checkpoint_path=/path/to/checkpoint.ckpt")
        return
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ Error: Checkpoint not found: {checkpoint_path}")
        return
    
    print("🔍 DINOv3+Mask2Former Model Evaluation with Hydra")
    print("=" * 60)
    print(f"📁 Run directory: {os.getcwd()}")
    print(f"📂 Checkpoint: {checkpoint_path}")
    print(f"🎯 Dataset: {cfg.data.name}")
    print("=" * 60)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.set_float32_matmul_precision(cfg.training.precision)
    
    # Setup processor
    processor = AutoImageProcessor.from_pretrained(
        cfg.model.processor.name,
        do_reduce_labels=cfg.model.processor.do_reduce_labels,
        ignore_index=cfg.model.processor.ignore_index,
        size={"height": cfg.data.image_size, "width": cfg.data.image_size}
    )
    
    # Create validation dataset
    val_dir = os.path.join(cfg.data.dataset_root, 'Val')
    val_dataset = LoveDADataset(
        val_dir, 
        processor
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=cfg.data.batch_size, 
        shuffle=False, 
        num_workers=cfg.data.num_workers,
        collate_fn=collate_fn,
        pin_memory=cfg.data.pin_memory
    )
    
    print(f"📊 Validation dataset: {len(val_dataset)} samples")
    print(f"📊 Validation batches: {len(val_loader)}")
    
    # Load model from checkpoint
    print("📂 Loading trained model...")
    model = SegmentationLightningModule.load_from_checkpoint(
        checkpoint_path,
        cfg=cfg
    )
    model = model.to(device)
    model.eval()
    
    # Setup metrics based on configuration
    metrics = {}
    if cfg.training.validation.metrics.include_background:
        metrics['val_mean_iou'] = JaccardIndex(
            task='multiclass', 
            num_classes=cfg.model.num_classes, 
            ignore_index=255
        ).to(device)
    
    if cfg.training.validation.metrics.exclude_background:
        metrics['val_mean_iou_no_bg'] = JaccardIndex(
            task='multiclass', 
            num_classes=cfg.model.num_classes - 1,
            ignore_index=255
        ).to(device)
    
    print("🧪 Running evaluation on validation set...")
    print("-" * 60)
    
    # Evaluation loop
    with torch.no_grad():
        for batch_idx, batch in enumerate(tqdm(val_loader, desc='Evaluating')):
            pixel_values = batch['pixel_values'].to(device)
            
            # Forward pass
            outputs = model.model(pixel_values=pixel_values)
            
            # Post-process predictions
            original_sizes = [tuple(img.shape[-2:]) for img in pixel_values]
            predicted_maps = processor.post_process_semantic_segmentation(
                outputs, target_sizes=original_sizes
            )
            
            # Reconstruct ground truth
            ground_truth_maps = []
            for i in range(len(pixel_values)):
                gt_map = torch.full_like(predicted_maps[i], 255)
                for mask, class_id in zip(batch['mask_labels'][i], batch['class_labels'][i]):
                    gt_map[mask.bool()] = class_id.item()
                ground_truth_maps.append(gt_map)
            
            # Clamp predictions and convert to tensors
            pred_maps_clamped = [torch.clamp(pred_map, 0, cfg.model.num_classes - 1) for pred_map in predicted_maps]
            preds_tensor = torch.stack(pred_maps_clamped).to(device).long()
            gt_tensor = torch.stack(ground_truth_maps).to(device).long()
            
            # Update metrics based on configuration
            if 'val_mean_iou' in metrics:
                metrics['val_mean_iou'].update(preds_tensor, gt_tensor)
            
            if 'val_mean_iou_no_bg' in metrics:
                # Prepare tensors for no-background metric
                preds_no_bg = preds_tensor.clone()
                gt_no_bg = gt_tensor.clone()
                
                for original_class in range(cfg.model.num_classes):
                    if original_class == 0:  # background -> ignore
                        preds_no_bg[preds_tensor == original_class] = 255
                        gt_no_bg[gt_tensor == original_class] = 255
                    else:  # classes 1-6 -> 0-5
                        preds_no_bg[preds_tensor == original_class] = original_class - 1
                        gt_no_bg[gt_tensor == original_class] = original_class - 1
                
                metrics['val_mean_iou_no_bg'].update(preds_no_bg, gt_no_bg)
            
            # Show progress every 50 batches
            if (batch_idx + 1) % 50 == 0:
                progress_metrics = {}
                for name, metric in metrics.items():
                    progress_metrics[name] = metric.compute().item()
                
                progress_str = " | ".join([f"{name}={score:.4f}" for name, score in progress_metrics.items()])
                print(f"  Batch {batch_idx + 1}/{len(val_loader)}: {progress_str}")
    
    # Compute final results
    final_results = {}
    for name, metric in metrics.items():
        final_results[name] = metric.compute().item()
    
    print("=" * 60)
    print("🏆 FINAL EVALUATION RESULTS")
    print("=" * 60)
    print(f"Model: {cfg.model.name}")
    print(f"Dataset: {cfg.data.name} Validation Set")
    print(f"Samples Evaluated: {len(val_dataset)}")
    print()
    
    # Display results based on configuration
    if 'val_mean_iou' in final_results:
        miou_all = final_results['val_mean_iou']
        print(f"📈 Including Background (all {cfg.model.num_classes} classes):")
        print(f"  Mean IoU: {miou_all:.4f} ({miou_all:.1%})")
    
    if 'val_mean_iou_no_bg' in final_results:
        miou_no_bg = final_results['val_mean_iou_no_bg']
        print(f"📈 Excluding Background ({cfg.model.num_classes - 1} semantic classes):")
        print(f"  Mean IoU: {miou_no_bg:.4f} ({miou_no_bg:.1%})")
        print(f"  Classes: {', '.join(cfg.data.class_names[1:])}")
    
    # Performance comparison
    if len(final_results) == 2:
        miou_all = final_results['val_mean_iou']
        miou_no_bg = final_results['val_mean_iou_no_bg']
        print()
        print("📊 Comparison:")
        print(f"  Difference: {miou_no_bg - miou_all:+.4f}")
        if miou_no_bg > miou_all:
            print("  → Semantic classes perform BETTER than overall average")
        else:
            print("  → Background class performs BETTER than semantic classes")
    
    # Performance assessment
    primary_score = final_results.get(cfg.training.validation.primary_metric, 0)
    print()
    print("🎯 Performance Assessment:")
    if primary_score > 0.5:
        assessment = "🏆 Outstanding performance!"
    elif primary_score > 0.4:
        assessment = "🏆 Excellent performance!"
    elif primary_score > 0.3:
        assessment = "✅ Strong performance!"
    elif primary_score > 0.2:
        assessment = "📈 Good performance!"
    else:
        assessment = "🔄 Room for improvement"
    print(f"  {assessment}")
    
    # Save results
    results_summary = {
        "model": cfg.model.name,
        "dataset": cfg.data.name,
        "checkpoint_path": checkpoint_path,
        "evaluation_results": final_results,
        "primary_metric": cfg.training.validation.primary_metric,
        "primary_score": primary_score,
        "num_classes": cfg.model.num_classes,
        "image_size": f"{cfg.data.image_size}x{cfg.data.image_size}",
        "samples_evaluated": len(val_dataset),
        "config_used": OmegaConf.to_yaml(cfg)
    }
    
    results_path = Path("evaluation_results.json")
    with open(results_path, "w") as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"📄 Detailed results saved to: {results_path}")
    print("=" * 60)
    print("✅ Evaluation complete!")


if __name__ == "__main__":
    main() 