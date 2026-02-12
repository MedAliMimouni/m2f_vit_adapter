"""
Approach 1: Custom Backbone Wrapper for DINOv2 + DINOv3_Adapter with Mask2Former

This approach creates a custom backbone that wraps your DINOv2 + DINOv3_Adapter
using Hugging Face's BackboneMixin, allowing seamless integration with Mask2Former.
"""

import torch
import torch.nn as nn
from transformers import (
    Mask2FormerForUniversalSegmentation, 
    Mask2FormerConfig,
    AutoImageProcessor,
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

class DINOv2AdapterBackboneConfig(PretrainedConfig, BackboneConfigMixin):
    """
    Configuration for DINOv2 + DINOv3_Adapter as a backbone.
    """
    model_type = "dinov2_adapter_backbone"
    
    def __init__(
        self,
        dinov2_model_name="dinov2_vitb14",
        interaction_indexes=[2, 5, 8, 11],
        pretrain_size=224,  # DINOv2's actual training resolution
        conv_inplane=64,
        n_points=4,
        deform_num_heads=16,
        drop_path_rate=0.3,
        with_cp=True,
        embed_dim=768,  # ViT-Base embedding dimension
        feature_strides=[4, 8, 16, 32],  # Feature map strides
        **kwargs
    ):
        # DINOv2 + Adapter configuration
        self.dinov2_model_name = dinov2_model_name
        self.interaction_indexes = interaction_indexes
        self.pretrain_size = pretrain_size
        self.conv_inplane = conv_inplane
        self.n_points = n_points
        self.deform_num_heads = deform_num_heads
        self.drop_path_rate = drop_path_rate
        self.with_cp = with_cp
        self.embed_dim = embed_dim
        
        # BackboneMixin required attributes - must be set before calling super().__init__
        self.feature_strides = feature_strides
        self.num_channels = embed_dim
        
        # Define stage names first (required by BackboneConfigMixin)
        self.stage_names = ["stage1", "stage2", "stage3", "stage4"]
        
        # Call parent constructors
        super().__init__(**kwargs)
        
        # Now set out_features and out_indices (after stage_names is defined)
        self.out_features = ["stage1", "stage2", "stage3", "stage4"]  # Use stage names instead of "1", "2", etc.
        self.out_indices = [0, 1, 2, 3]


class DINOv2AdapterBackbone(nn.Module, BackboneMixin):
    """
    Custom backbone that wraps DINOv2 + DINOv3_Adapter for use with Mask2Former.
    """
    
    def __init__(self, config: DINOv2AdapterBackboneConfig):
        super().__init__()
        self.config = config
        
        # Load DINOv2 backbone
        print(f"Loading DINOv2 model: {config.dinov2_model_name}")
        self.dinov2_backbone = torch.hub.load(
            'facebookresearch/dinov2', 
            config.dinov2_model_name
        )
        
        # Create DINOv3_Adapter
        self.adapter = DINOv3_Adapter(
            backbone=self.dinov2_backbone,
            interaction_indexes=config.interaction_indexes,
            pretrain_size=config.pretrain_size,  # Use config value
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
        Forward pass through DINOv2 + Adapter.
        
        Args:
            pixel_values: Input tensor of shape (batch_size, 3, height, width)
            output_hidden_states: Whether to return hidden states (optional)
            return_dict: Whether to return BackboneOutput (optional)
            
        Returns:
            BackboneOutput: Contains feature_maps tuple ordered by stride
        """
        # Get multi-scale features from adapter as a dictionary
        features_dict = self.adapter(pixel_values)
        
        # Convert adapter output {"1": f1, "2": f2, "3": f3, "4": f4} to ordered tuple
        # Order by keys to ensure consistent stride ordering (lowest to highest stride)
        ordered_keys = sorted(features_dict.keys())  # ["1", "2", "3", "4"]
        feature_maps = tuple(features_dict[key] for key in ordered_keys)
        return BackboneOutput(
            feature_maps=feature_maps,
            hidden_states=tuple([feature_maps]) if output_hidden_states else None,
            attentions=None,
        )


def create_dinov2_mask2former(
    dinov2_model_name="dinov2_vitb14",
    interaction_indexes=[2, 5, 8, 11],
    pretrain_size=224,
    mask2former_config_name="facebook/mask2former-swin-base-coco-panoptic",
    num_classes=133,  # COCO panoptic classes
    **kwargs
):
    """
    Create a Mask2Former model with DINOv2 + DINOv3_Adapter backbone.
    
    Args:
        dinov2_model_name: DINOv2 model variant
        interaction_indexes: Interaction layers for adapter
        pretrain_size: Input size for adapter
        mask2former_config_name: Base Mask2Former config to modify
        num_classes: Number of segmentation classes
        **kwargs: Additional arguments for adapter
        
    Returns:
        tuple: (model, processor, backbone_config)
    """
    
    # 1. Create backbone configuration
    backbone_config = DINOv2AdapterBackboneConfig(
        dinov2_model_name=dinov2_model_name,
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
    # Note: This requires modifying how Mask2Former initializes its backbone
    # We'll need to manually set the backbone after model creation
    model = Mask2FormerForUniversalSegmentation(mask2former_config)
    
    # Replace the backbone with our custom one
    custom_backbone = DINOv2AdapterBackbone(backbone_config)
    model.model.backbone = custom_backbone
    
    # 5. Get processor and configure it for the correct number of classes
    # Create a processor with configuration matching our model
    processor = AutoImageProcessor.from_pretrained(
        mask2former_config_name,
        num_labels=num_classes,  # Set the correct number of labels
        id2label={i: str(i) for i in range(num_classes)},  # Create simple id2label mapping
        label2id={str(i): i for i in range(num_classes)}   # Create simple label2id mapping
    )
    
    return model, processor, backbone_config


def main_example():
    """
    Example usage of DINOv2 + Adapter with Mask2Former.
    """
    print("Creating DINOv2 + Adapter + Mask2Former model...")
    
    # Create the integrated model
    model, processor, backbone_config = create_dinov2_mask2former(
        dinov2_model_name="dinov2_vitb14",
        interaction_indexes=[2, 5, 8, 11],  # For ViT-B/14
        pretrain_size=224,  # DINOv2's actual training resolution
        num_classes=133  # COCO panoptic
    )
    

    
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)
    print(f"Original image size: {image.size}")
    
    # Preprocess image - Use DINOv2's native training size
    # Manual preprocessing to ensure exact size control
    # TODO: this will be investigated latter
    inputs = processor(images=image, return_tensors="pt")
    # from torchvision import transforms
    # transform = transforms.Compose([
    #     transforms.Resize((224, 224)),
    #     transforms.ToTensor(),
    #     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    # ])
    # inputs = {"pixel_values": transform(image).unsqueeze(0)}
    print("inputs['pixel_values'].shape", inputs["pixel_values"].shape)
    # Run inference
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    
    with torch.no_grad():
        # Move inputs to device (inputs is now a dict, not a tensor)
        device_inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model(**device_inputs)
    
    # Post-process results (use original processor for post-processing)
    result = processor.post_process_panoptic_segmentation(
        outputs, 
        target_sizes=[image.size[::-1]]
    )[0]
    
    print("✅ Success! DINOv2 + Adapter + Mask2Former inference completed")
    print(f"Segmentation map shape: {result['segmentation'].shape}")
    print(f"Number of segments: {len(result['segments_info'])}")
    
    # Save the results
    save_segmentation_results(image, result, model.config if hasattr(model, 'config') else None)
    
    return model, result


def save_segmentation_results(original_image, segmentation_result, model_config=None):
    """
    Save the segmentation results as images.
    
    Args:
        original_image: PIL Image - the original input image
        segmentation_result: dict - result from post_process_panoptic_segmentation
        model_config: optional model configuration for label mapping
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from collections import defaultdict
    import numpy as np
    
    segmentation_map = segmentation_result['segmentation']
    segments_info = segmentation_result['segments_info']
    
    print(f"\n📁 Saving segmentation results...")
    
    # 1. Save original image
    original_image.save("original_image.jpg")
    print("✅ Saved: original_image.jpg")
    
    # 2. Save raw segmentation map
    seg_array = segmentation_map.cpu().numpy() if hasattr(segmentation_map, 'cpu') else np.array(segmentation_map)
    
    # Normalize segmentation map for visualization
    if seg_array.max() > 0:
        seg_normalized = (seg_array / seg_array.max() * 255).astype(np.uint8)
    else:
        seg_normalized = seg_array.astype(np.uint8)
    
    seg_image = Image.fromarray(seg_normalized)
    seg_image.save("segmentation_map.png")
    print("✅ Saved: segmentation_map.png")
    
    # 3. Create colored visualization
    if len(segments_info) > 0:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        
        # Original image
        ax1.imshow(original_image)
        ax1.set_title("Original Image", fontsize=14)
        ax1.axis('off')
        
        # Raw segmentation map
        ax2.imshow(seg_array, cmap='viridis')
        ax2.set_title("Segmentation Map", fontsize=14)
        ax2.axis('off')
        
        # Colored segmentation with legend
        colored_seg = np.zeros((*seg_array.shape, 3), dtype=np.uint8)
        instances_counter = defaultdict(int)
        handles = []
        
        # Generate colors for each segment
        np.random.seed(42)  # For consistent colors
        colors = np.random.rand(len(segments_info), 3)
        
        for i, segment in enumerate(segments_info):
            segment_id = segment['id']
            segment_label_id = segment['label_id']
            
            # Get label name if available
            label_name = f"class_{segment_label_id}"
            if model_config and hasattr(model_config, 'id2label') and segment_label_id in model_config.id2label:
                label_name = model_config.id2label[segment_label_id]
            
            # Create mask for this segment
            mask = seg_array == segment_id
            if mask.any():
                color = colors[i]
                colored_seg[mask] = (color * 255).astype(np.uint8)
                
                # Add to legend
                label = f"{label_name}-{instances_counter[segment_label_id]}"
                instances_counter[segment_label_id] += 1
                handles.append(mpatches.Patch(color=color, label=label))
        
        ax3.imshow(colored_seg)
        ax3.set_title("Colored Segmentation", fontsize=14)
        ax3.axis('off')
        
        # Add legend if we have segments
        if handles:
            ax3.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig("segmentation_visualization.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("✅ Saved: segmentation_visualization.png")
        
    else:
        # If no segments detected, save a simple comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        ax1.imshow(original_image)
        ax1.set_title("Original Image", fontsize=14)
        ax1.axis('off')
        
        ax2.imshow(seg_array, cmap='gray')
        ax2.set_title("Segmentation Map (No segments detected)", fontsize=14)
        ax2.axis('off')
        
        plt.tight_layout()
        plt.savefig("segmentation_comparison.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("✅ Saved: segmentation_comparison.png")
    
    # 4. Save segment info as text
    with open("segmentation_info.txt", "w") as f:
        f.write("DINOv2 + Adapter + Mask2Former Segmentation Results\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Original image size: {original_image.size}\n")
        f.write(f"Segmentation map shape: {segmentation_map.shape}\n")
        f.write(f"Number of segments detected: {len(segments_info)}\n\n")
        
        if segments_info:
            f.write("Detected Segments:\n")
            f.write("-" * 20 + "\n")
            for i, segment in enumerate(segments_info):
                f.write(f"Segment {i+1}:\n")
                f.write(f"  ID: {segment['id']}\n")
                f.write(f"  Label ID: {segment['label_id']}\n")
                if 'area' in segment:
                    f.write(f"  Area: {segment['area']}\n")
                f.write("\n")
        else:
            f.write("No segments detected. This is expected for an untrained model.\n")
            f.write("Consider:\n")
            f.write("- Fine-tuning on your target dataset\n")
            f.write("- Adjusting confidence thresholds\n")
            f.write("- Using a different pre-trained model\n")
    
    print("✅ Saved: segmentation_info.txt")
    print(f"\n📊 Summary:")
    print(f"   - Original image: {original_image.size}")
    print(f"   - Segmentation shape: {segmentation_map.shape}")
    print(f"   - Segments detected: {len(segments_info)}")
    print(f"   - Files saved: 4 files in current directory")


if __name__ == "__main__":
    main_example() 