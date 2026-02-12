"""
DINOv3-ViT-L/16 + DINOv3_Adapter with Mask2Former Integration

This integration uses DINOv3-ViT-L/16 from HuggingFace instead of DINOv2.
Key differences:
- Patch size: 16 (instead of 14)
- Token structure: 196 patches + 1 CLS + 4 registers = 201 tokens
- Model: facebook/dinov3-vitl16-pretrain-sat493m
- Embedding dim: 1024 (ViT-Large)
"""

import torch
import torch.nn as nn
from transformers import (
    Mask2FormerForUniversalSegmentation, 
    Mask2FormerConfig,
    AutoImageProcessor,
    AutoModel,
    PretrainedConfig
)
from transformers.utils import BackboneMixin, BackboneConfigMixin
from transformers.modeling_outputs import BackboneOutput
from models.backbone.dinov3_adapter import DINOv3_Adapter

# Load test image
from PIL import Image
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

# HuggingFace token for DINOv3 access
HF_TOKEN = os.environ.get("HF_TOKEN", "")

class DINOv3AdapterBackboneConfig(PretrainedConfig, BackboneConfigMixin):
    """
    Configuration for DINOv3-ViT-L/16 + DINOv3_Adapter as a backbone.
    """
    model_type = "dinov3_adapter_backbone"
    
    def __init__(
        self,
        dinov3_model_name="facebook/dinov3-vitl16-pretrain-sat493m",
        interaction_indexes=[4, 11, 17, 23],  # For ViT-Large (24 layers)
        pretrain_size=224,  # DINOv3's training resolution
        conv_inplane=64,
        n_points=4,
        deform_num_heads=16,
        drop_path_rate=0.3,
        with_cp=True,
        embed_dim=1024,  # ViT-Large embedding dimension
        patch_size=16,    # DINOv3-ViT-L/16 patch size
        feature_strides=[4, 8, 16, 32],  # Feature map strides
        **kwargs
    ):
        # DINOv3 + Adapter configuration
        self.dinov3_model_name = dinov3_model_name
        self.interaction_indexes = interaction_indexes
        self.pretrain_size = pretrain_size
        self.conv_inplane = conv_inplane
        self.n_points = n_points
        self.deform_num_heads = deform_num_heads
        self.drop_path_rate = drop_path_rate
        self.with_cp = with_cp
        self.embed_dim = embed_dim
        self.patch_size = patch_size
        
        # BackboneMixin required attributes - must be set before calling super().__init__
        self.feature_strides = feature_strides
        self.num_channels = embed_dim
        
        # Define stage names first (required by BackboneConfigMixin)
        self.stage_names = ["stage1", "stage2", "stage3", "stage4"]
        
        # Call parent constructors
        super().__init__(**kwargs)
        
        # Now set out_features and out_indices (after stage_names is defined)
        self.out_features = self.stage_names
        self.out_indices = [0, 1, 2, 3]


class DINOv3CompatibilityWrapper:
    """
    Wrapper to make DINOv3 compatible with DINOv3_Adapter which expects DINOv2-style attributes.
    """
    def __init__(self, dinov3_model):
        self.model = dinov3_model
        
        # Add DINOv2-style attributes expected by the adapter
        self.embed_dim = dinov3_model.config.hidden_size  # 1024 for ViT-Large
        self.patch_size = dinov3_model.config.patch_size  # 16
        self.num_layers = dinov3_model.config.num_hidden_layers  # 24
        
        # Forward all other attributes to the wrapped model
    def __getattr__(self, name):
        return getattr(self.model, name)
    
    def __call__(self, *args, **kwargs):
        return self.model(*args, **kwargs)


class DINOv3AdapterBackbone(nn.Module, BackboneMixin):
    """
    Custom backbone that wraps DINOv3-ViT-L/16 + DINOv3_Adapter for use with Mask2Former.
    """
    
    def __init__(self, config: DINOv3AdapterBackboneConfig):
        super().__init__()
        self.config = config
        
        # Load DINOv3 backbone using HuggingFace
        print(f"Loading DINOv3 model: {config.dinov3_model_name}")
        dinov3_model = AutoModel.from_pretrained(
            config.dinov3_model_name,
            token=HF_TOKEN,
            device_map="auto"
        )
        
        # Wrap DINOv3 for compatibility with adapter
        self.dinov3_backbone = DINOv3CompatibilityWrapper(dinov3_model)
        
        # Print model info
        print(f"DINOv3 embedding dim: {self.dinov3_backbone.embed_dim}")
        print(f"DINOv3 patch size: {self.dinov3_backbone.patch_size}")
        print(f"DINOv3 layers: {self.dinov3_backbone.num_layers}")
        print(f"Interaction indexes: {config.interaction_indexes}")
        
        # Create DINOv3_Adapter
        self.adapter = DINOv3_Adapter(
            backbone=self.dinov3_backbone,
            interaction_indexes=config.interaction_indexes,
            pretrain_size=config.pretrain_size,
            conv_inplane=config.conv_inplane,
            n_points=config.n_points,
            deform_num_heads=config.deform_num_heads,
            drop_path_rate=config.drop_path_rate,
            with_cp=config.with_cp
        )
        
        # BackboneMixin required attributes  
        self.num_features = len(config.out_features)
        
        # Store stage names for easy access
        self.stage_names = config.stage_names
        
    def forward(self, pixel_values, output_hidden_states=None, return_dict=None):
        """
        Forward pass through DINOv3 + Adapter backbone.
        
        Args:
            pixel_values: Input images [B, C, H, W]
            
        Returns:
            BackboneOutput with multi-scale features
        """
        # Get multi-scale features from adapter
        features = self.adapter(pixel_values)
        
        # Convert to the format expected by BackboneOutput
        # features is a list of [feat1, feat2, feat3, feat4] corresponding to different scales
        feature_maps = tuple(features)
        
        if not return_dict:
            return feature_maps
            
        return BackboneOutput(
            feature_maps=feature_maps,
            hidden_states=feature_maps if output_hidden_states else None,
            attentions=None,
        )


def create_dinov3_mask2former(
    dinov3_model_name="facebook/dinov3-vitl16-pretrain-sat493m",
    interaction_indexes=[4, 11, 17, 23],  # For ViT-Large (24 layers)
    pretrain_size=224,
    mask2former_config_name="facebook/mask2former-swin-base-coco-panoptic",
    num_classes=133,  # COCO panoptic classes
    **kwargs
):
    """
    Create a Mask2Former model with DINOv3-ViT-L/16 + DINOv3_Adapter backbone.
    
    Args:
        dinov3_model_name: DINOv3 model variant
        interaction_indexes: Interaction layers for adapter (for 24-layer ViT-Large)
        pretrain_size: Input size for adapter
        mask2former_config_name: Base Mask2Former config to modify
        num_classes: Number of segmentation classes
        **kwargs: Additional arguments for adapter
        
    Returns:
        tuple: (model, processor, backbone_config)
    """
    
    # 1. Create backbone configuration
    backbone_config = DINOv3AdapterBackboneConfig(
        dinov3_model_name=dinov3_model_name,
        interaction_indexes=interaction_indexes,
        pretrain_size=pretrain_size,
        **kwargs
    )
    
    # 2. Load base Mask2Former configuration
    base_config = Mask2FormerConfig.from_pretrained(mask2former_config_name)
    
    # 3. Create a new config by copying the base config and modifying what we need
    mask2former_config_dict = base_config.to_dict()
    
    # Update config for our backbone
    mask2former_config_dict.update({
        "feature_strides": [4, 8, 16, 32],  # Match our adapter output
        "num_labels": num_classes,
        # Remove backbone_config to avoid CONFIG_MAPPING lookup
        "backbone_config": None,
        "backbone": None,
        "use_pretrained_backbone": False,
    })
    
    # Create the final config without backbone_config to avoid the lookup error
    mask2former_config = Mask2FormerConfig(**mask2former_config_dict)
    
    # 4. Create Mask2Former model with custom backbone
    model = Mask2FormerForUniversalSegmentation(mask2former_config)
    
    # Replace the backbone with our custom one
    custom_backbone = DINOv3AdapterBackbone(backbone_config)
    model.model.backbone = custom_backbone
    
    # 5. Get processor and configure it for the correct number of classes
    # For DINOv3 with patch size 16, optimal sizes are multiples of 16
    processor = AutoImageProcessor.from_pretrained(
        mask2former_config_name,
        num_labels=num_classes,
        id2label={i: str(i) for i in range(num_classes)},
        label2id={str(i): i for i in range(num_classes)},
        size={"height": 224, "width": 224}  # Start with 224x224 (14x14 patches)
    )
    
    return model, processor, backbone_config


def calculate_optimal_sizes_for_dinov3():
    """
    Calculate optimal image sizes for DINOv3-ViT-L/16.
    Sizes must be divisible by patch_size=16.
    """
    patch_size = 16
    base_sizes = [224, 256, 320, 384, 448, 512, 576, 640]
    
    print("DINOv3-ViT-L/16 Optimal Sizes:")
    print("=" * 40)
    print(f"{'Size':<8} {'Patches':<12} {'Total Patches':<15} {'vs 224x224':<10}")
    print("-" * 45)
    
    baseline_patches = (224 // patch_size) ** 2  # 14x14 = 196
    
    for size in base_sizes:
        if size % patch_size == 0:  # Only perfect divisions
            patches_per_side = size // patch_size
            total_patches = patches_per_side ** 2
            ratio = total_patches / baseline_patches
            
            print(f"{size:<8} {patches_per_side}x{patches_per_side:<7} {total_patches:<15} {ratio:.2f}x")


def main_example():
    """
    Example usage of DINOv3-ViT-L/16 + Adapter with Mask2Former.
    """
    print("Creating DINOv3-ViT-L/16 + Adapter + Mask2Former model...")
    print("=" * 60)
    
    # Show optimal sizes
    calculate_optimal_sizes_for_dinov3()
    
    print(f"\n{'Creating model...'}")
    
    # Create the integrated model
    model, processor, backbone_config = create_dinov3_mask2former(
        dinov3_model_name="facebook/dinov3-vitl16-pretrain-sat493m",
        interaction_indexes=[4, 8, 12, 16],  # For ViT-Large (24 layers)
        pretrain_size=224,  # Start with DINOv3's training resolution
        num_classes=7  # LoveDA classes
    )
    
    print("✅ Model created successfully!")
    
    # Test with sample image
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)
    print(f"Original image size: {image.size}")
    
    # Preprocess image
    inputs = processor(images=image, return_tensors="pt")
    print(f"Processed shape: {inputs['pixel_values'].shape}")
    
    # Verify patch calculation
    h, w = inputs['pixel_values'].shape[2:]
    patch_size = 16
    patches_h = h // patch_size
    patches_w = w // patch_size
    total_patches = patches_h * patches_w
    
    print(f"Patch calculation: {h}x{w} ÷ {patch_size} = {patches_h}x{patches_w} = {total_patches} patches")
    print(f"Expected tokens: {total_patches} + 1 CLS + 4 registers = {total_patches + 5}")
    
    # Run inference
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    
    with torch.no_grad():
        device_inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model(**device_inputs)
    
    print("✅ Success! DINOv3-ViT-L/16 + Adapter + Mask2Former inference completed")
    
    if hasattr(outputs, 'class_queries_logits'):
        print(f"Class queries shape: {outputs.class_queries_logits.shape}")
    if hasattr(outputs, 'masks_queries_logits'):
        print(f"Mask queries shape: {outputs.masks_queries_logits.shape}")


if __name__ == "__main__":
    main_example() 