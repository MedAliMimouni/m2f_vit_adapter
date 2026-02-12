"""
DINOv3-ViT-L/16 + DINOv3_Adapter with Mask2Former Integration

This integration uses DINOv3-ViT-L/16 from HuggingFace instead of DINOv2.
Key differences:
- Patch size: 16 (instead of 14)
- Token structure: 196 patches + 1 CLS + 4 registers = 201 tokens
- Model: facebook/dinov3-vitl16-pretrain-sat493m
- Embedding dim: 1024 (ViT-Large)
"""

import os
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
    Implements get_intermediate_layers() to extract features at specific transformer layers.
    """
    def __init__(self, dinov3_model):
        self.model = dinov3_model

        # Add DINOv2-style attributes expected by the adapter
        self.embed_dim = dinov3_model.config.hidden_size  # 1024 for ViT-Large
        self.patch_size = dinov3_model.config.patch_size  # 16
        self.num_layers = dinov3_model.config.num_hidden_layers  # 24

    def __getattr__(self, name):
        return getattr(self.model, name)

    def __call__(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def get_intermediate_layers(self, x, n, return_class_token=True):
        """
        Extract intermediate layer features from DINOv3.

        This mimics the DINOv2 torch.hub API for compatibility with DINOv3_Adapter.

        Args:
            x: Input tensor of shape (B, C, H, W)
            n: List of layer indices to extract features from (e.g., [4, 11, 17, 23])
            return_class_token: If True, return (patch_tokens, cls_token) tuples

        Returns:
            List of tuples (patch_tokens, cls_token) for each requested layer
        """
        # Forward through the model with output_hidden_states=True
        outputs = self.model(x, output_hidden_states=True)

        # hidden_states is a tuple of (embedding_output, layer_1, layer_2, ..., layer_N)
        # Index 0 is the embedding output, indices 1-N are the transformer layer outputs
        hidden_states = outputs.hidden_states

        results = []
        for layer_idx in n:
            # hidden_states[0] is embedding, hidden_states[1] is layer 0, etc.
            # So layer_idx=4 means we want hidden_states[5] (after 4 transformer layers)
            # But HuggingFace uses 0-indexed layers, so layer 4 = hidden_states[4+1] = hidden_states[5]
            # Actually, let's check: hidden_states has len = num_layers + 1
            # hidden_states[0] = embeddings
            # hidden_states[i] = output after layer i-1 (0-indexed)
            # So to get output after layer_idx (0-indexed), we need hidden_states[layer_idx + 1]
            state = hidden_states[layer_idx + 1]  # (B, num_tokens, hidden_size)

            # DINOv3 token structure: [CLS, patch_1, ..., patch_N, reg_1, ..., reg_4]
            # For DINOv3-ViT-L/16: CLS at 0, patches at 1:N+1, registers at N+1:N+5
            # The adapter expects: patch_tokens (without CLS/registers), cls_token

            cls_token = state[:, 0, :]  # (B, hidden_size) - squeezed to match DINOv2 API

            # Remove CLS (index 0) and register tokens (last 4 tokens)
            # Registers are at the end for DINOv3
            num_register_tokens = getattr(self.model.config, 'num_register_tokens', 4)
            if num_register_tokens > 0:
                patch_tokens = state[:, 1:-num_register_tokens, :]  # (B, num_patches, hidden_size)
            else:
                patch_tokens = state[:, 1:, :]  # (B, num_patches, hidden_size)

            if return_class_token:
                results.append((patch_tokens, cls_token))
            else:
                results.append(patch_tokens)

        return results


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
            trust_remote_code=True,
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


def _count_params(module):
    """Count total parameters in a module."""
    return sum(p.numel() for p in module.parameters())


def _log_weight_status(component_name, total_params, pretrained_params, random_params):
    """Log the weight status for a component."""
    pretrained_pct = (pretrained_params / total_params * 100) if total_params > 0 else 0
    random_pct = (random_params / total_params * 100) if total_params > 0 else 0

    status = "✅ PRETRAINED" if pretrained_pct > 95 else "⚠️ PARTIAL" if pretrained_pct > 0 else "❌ RANDOM"

    print(f"  {component_name}:")
    print(f"    Total params:      {total_params:>12,}")
    print(f"    Pretrained:        {pretrained_params:>12,} ({pretrained_pct:5.1f}%) {status}")
    print(f"    Random/Reinit:     {random_params:>12,} ({random_pct:5.1f}%)")
    return pretrained_params, random_params


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

    print("\n" + "=" * 70)
    print("🏗️  CREATING DINOv3 + ViT-Adapter + Mask2Former MODEL")
    print("=" * 70)

    # =========================================================================
    # STEP 1: Create backbone configuration
    # =========================================================================
    backbone_config = DINOv3AdapterBackboneConfig(
        dinov3_model_name=dinov3_model_name,
        interaction_indexes=interaction_indexes,
        pretrain_size=pretrain_size,
        **kwargs
    )

    # =========================================================================
    # STEP 2: Load PRETRAINED Mask2Former (not from config!)
    # =========================================================================
    print("\n📦 Loading Mask2Former with PRETRAINED weights...")
    print(f"   Base model: {mask2former_config_name}")
    print(f"   Target classes: {num_classes}")

    # Load base config and modify for our needs
    base_config = Mask2FormerConfig.from_pretrained(mask2former_config_name)
    base_config.num_labels = num_classes

    # Use from_pretrained to get pretrained weights!
    # ignore_mismatched_sizes=True allows different num_classes
    model = Mask2FormerForUniversalSegmentation.from_pretrained(
        mask2former_config_name,
        config=base_config,
        ignore_mismatched_sizes=True,
    )

    # =========================================================================
    # STEP 3: Create custom backbone with PRETRAINED DINOv3
    # =========================================================================
    print("\n📦 Creating DINOv3 + ViT-Adapter backbone...")
    custom_backbone = DINOv3AdapterBackbone(backbone_config)

    # =========================================================================
    # STEP 4: Log weight status BEFORE replacing backbone
    # =========================================================================
    print("\n" + "-" * 70)
    print("📊 WEIGHT STATUS SUMMARY")
    print("-" * 70)

    total_pretrained = 0
    total_random = 0

    # --- DINOv3 Backbone (inside our custom backbone) ---
    print("\n🧠 DINOv3-ViT-L/16 BACKBONE:")
    dinov3_params = _count_params(custom_backbone.dinov3_backbone.model)
    pretrained, random = _log_weight_status(
        "DINOv3-ViT-L/16 (frozen)",
        dinov3_params,
        dinov3_params,  # All pretrained from HuggingFace
        0
    )
    total_pretrained += pretrained
    total_random += random

    # --- ViT-Adapter (randomly initialized) ---
    print("\n🔧 VIT-ADAPTER:")
    # Count only the adapter's own parameters (not the backbone)
    # The backbone is stored as a non-Module wrapper, so we need to count adapter modules only
    adapter_only_params = 0
    for name, module in custom_backbone.adapter.named_modules():
        if name and not name.startswith('backbone'):
            adapter_only_params += sum(p.numel() for p in module.parameters(recurse=False))
    pretrained, random = _log_weight_status(
        "ViT-Adapter layers",
        adapter_only_params,
        0,  # All random - adapter is not pretrained
        adapter_only_params
    )
    total_pretrained += pretrained
    total_random += random

    # --- Mask2Former Pixel Decoder ---
    print("\n🎨 MASK2FORMER PIXEL DECODER:")
    pixel_decoder = model.model.pixel_level_module.decoder
    pixel_decoder_params = _count_params(pixel_decoder)
    pretrained, random = _log_weight_status(
        "Pixel Decoder (FPN + layers)",
        pixel_decoder_params,
        pixel_decoder_params,  # All pretrained from COCO
        0
    )
    total_pretrained += pretrained
    total_random += random

    # --- Mask2Former Transformer Decoder ---
    print("\n🔮 MASK2FORMER TRANSFORMER DECODER:")
    transformer_module = model.model.transformer_module
    transformer_params = _count_params(transformer_module)
    pretrained, random = _log_weight_status(
        "Transformer Decoder",
        transformer_params,
        transformer_params,  # All pretrained from COCO
        0
    )
    total_pretrained += pretrained
    total_random += random

    # --- Class Predictor (reinitialized due to different num_classes) ---
    print("\n🏷️  CLASS PREDICTOR:")
    class_predictor = model.class_predictor
    class_predictor_params = _count_params(class_predictor)
    pretrained, random = _log_weight_status(
        f"Class Predictor ({num_classes} classes)",
        class_predictor_params,
        0,  # Reinitialized due to num_classes mismatch
        class_predictor_params
    )
    total_pretrained += pretrained
    total_random += random

    # --- Swin Backbone (will be REPLACED) ---
    print("\n🔄 SWIN BACKBONE (to be replaced):")
    swin_encoder = model.model.pixel_level_module.encoder
    swin_params = _count_params(swin_encoder)
    print(f"  Swin-Base backbone:")
    print(f"    Total params:      {swin_params:>12,}")
    print(f"    Status:            ❌ WILL BE REPLACED by DINOv3 + Adapter")

    # =========================================================================
    # STEP 5: Replace backbone
    # =========================================================================
    print("\n" + "-" * 70)
    print("🔄 REPLACING BACKBONE...")
    print("-" * 70)

    # Replace the Swin encoder with our DINOv3 + Adapter backbone
    model.model.pixel_level_module.encoder = custom_backbone
    print("✅ Replaced pixel_level_module.encoder with DINOv3 + ViT-Adapter")

    # =========================================================================
    # STEP 6: Final summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("📊 FINAL WEIGHT SUMMARY")
    print("=" * 70)

    total_model_params = _count_params(model)
    print(f"\n  Total model parameters:     {total_model_params:>12,}")
    print(f"  ├── Pretrained:             {total_pretrained:>12,} ({total_pretrained/total_model_params*100:.1f}%)")
    print(f"  └── Random/Reinitialized:   {total_random:>12,} ({total_random/total_model_params*100:.1f}%)")

    print("\n  Component breakdown:")
    print(f"    • DINOv3 backbone:        {dinov3_params:>12,} (pretrained, frozen)")
    print(f"    • ViT-Adapter:            {adapter_only_params:>12,} (random, trainable)")
    print(f"    • M2F Pixel Decoder:      {pixel_decoder_params:>12,} (pretrained, trainable)")
    print(f"    • M2F Transformer:        {transformer_params:>12,} (pretrained, trainable)")
    print(f"    • Class Predictor:        {class_predictor_params:>12,} (reinitialized, trainable)")

    print("\n⚠️  NOTE: Pixel decoder input projections expect Swin channel dims")
    print("   (128, 256, 512, 1024) but adapter outputs 1024 at all scales.")
    print("   This will cause dimension mismatch at forward pass!")
    print("   TODO: Add projection layers to match Swin channel dimensions.")

    print("=" * 70 + "\n")

    # =========================================================================
    # STEP 7: Get processor
    # =========================================================================
    processor = AutoImageProcessor.from_pretrained(
        mask2former_config_name,
        num_labels=num_classes,
        id2label={i: str(i) for i in range(num_classes)},
        label2id={str(i): i for i in range(num_classes)},
        size={"height": 224, "width": 224}
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