# DINOv2 + Mask2Former Integration

A production-ready implementation that integrates DINOv2 backbones with the DINOv3_Adapter and Mask2Former for semantic segmentation. This implementation provides a clean, modular approach to building state-of-the-art segmentation models.

## 🎯 Key Features

- **Multi-scale Feature Extraction**: Provides 4 different scales suitable for dense prediction
- **Frozen Backbone Strategy**: DINOv2 backbone is frozen, only adapter layers (~50M parameters) are trainable
- **HuggingFace Compatible**: Seamless integration with the HuggingFace ecosystem
- **Memory Efficient**: Uses gradient checkpointing and optimized attention mechanisms
- **Production Ready**: Clean, modular architecture ready for training and deployment

## 🚀 Quick Start

### Installation
```bash
pip install torch torchvision transformers pillow matplotlib
```

### Basic Usage
```python
from dinov2_mask2former_integration import create_dinov2_mask2former
from PIL import Image
import requests

# Create the integrated model
model, processor, config = create_dinov2_mask2former(
    dinov2_model_name="dinov2_vitb14",
    interaction_indexes=[2, 5, 8, 11],
    pretrain_size=224,  # Critical: Must match DINOv2's training resolution
    num_classes=133     # COCO panoptic classes
)

# Load and process an image
url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)

# Run inference (see main script for complete preprocessing)
# ... preprocessing code ...
# outputs = model(**inputs)
# result = processor.post_process_panoptic_segmentation(outputs, target_sizes=[image.size[::-1]])[0]
```

### Complete Example
```bash
python example.py
```

This runs the complete pipeline and saves visualization results.

For the full implementation details, see `dinov2_mask2former_integration.py`.

## 📁 Directory Structure

```
dinov2mask2former/
├── example.py                           # 🎯 Simple usage example (start here!)
├── dinov2_mask2former_integration.py    # 🔧 Main implementation
├── README.md                            # This file  
├── models/                              # Core model implementations
│   ├── backbone/
│   │   └── dinov3_adapter.py           # DINOv3_Adapter implementation
│   └── utils/
│       └── ms_deform_attn.py           # Multi-scale deformable attention
└── debugging_and_examples/             # All debugging & development files
    ├── README.md                       # Guide to debugging files
    ├── alternative_approaches/         # Different implementation approaches
    ├── docs/                          # Comprehensive guides
    ├── outputs/                       # Generated test outputs
    └── setup_and_utils/               # Setup utilities
```

## 🔧 Architecture Overview

### Pipeline Flow:
```
Input Image (224×224)
    ↓
DINOv2 Backbone (frozen)
    ↓  
DINOv3_Adapter (trainable ~50M params)
    ↓
Multi-scale Features {"1": [768,56,56], "2": [768,28,28], "3": [768,14,14], "4": [768,7,7]}
    ↓
Mask2Former Head
    ↓
Segmentation Output
```

### Key Components:

1. **DINOv2 Backbone**: Pretrained vision transformer (frozen)
2. **DINOv3_Adapter**: Converts single-scale ViT features to multi-scale pyramid
3. **Mask2Former Head**: Universal segmentation head for panoptic/instance/semantic tasks

## ⚙️ Configuration Parameters

### Supported Backbones:
- **DINOv2-S/14**: `interaction_indexes=[2, 5, 8, 11]`
- **DINOv2-B/14**: `interaction_indexes=[2, 5, 8, 11]` (recommended)
- **DINOv2-L/14**: `interaction_indexes=[4, 11, 17, 23]`
- **DINOv2-G/14**: `interaction_indexes=[7, 15, 23, 31]`

### Critical Settings:
- **`pretrain_size=224`**: Must match DINOv2's training resolution
- **Input size**: 224×224 (or other multiples of 14: 280, 336, 392, 448)
- **Patch compatibility**: Ensure input_size ÷ 14 is an integer

## 🎯 Training Considerations

### Current Status:
- ✅ **Architecture**: Complete and tested
- ✅ **Feature extraction**: Multi-scale pyramid working
- ✅ **Inference pipeline**: Fully functional
- 📝 **Training**: Ready for training implementation (untrained head currently)

### For Training:
```python
# Add these components:
- Loss functions (cross-entropy, dice, focal)
- Data loaders for segmentation datasets
- Training loop with optimizer
- Learning rate scheduling
- Validation metrics
```

### Memory Management:
- Enable `with_cp=True` for gradient checkpointing
- Only adapter layers need gradients (~50M parameters)
- Recommended batch size: Adjust based on GPU memory
- Input resolution: 224×224 (optimal for DINOv2)

## 🐛 Troubleshooting

### Common Issues:

**1. Size Compatibility Errors**
```
AssertionError: Input image height X is not a multiple of patch height 14
```
**Solution**: Use input sizes divisible by 14 (224, 280, 336, 392, 448)

**2. Tensor Size Mismatch in Adapter**
```
RuntimeError: The size of tensor a (X) must match the size of tensor b (Y)
```
**Solution**: Set `pretrain_size=224` to match DINOv2's training resolution

**3. Black/Empty Segmentation**
- **Expected behavior** for untrained segmentation head
- Add training pipeline or load pretrained weights

### Debugging Resources:
See `debugging_and_examples/` directory for comprehensive debugging tools and guides.

## 📊 Performance

### Feature Extraction:
- **Input**: 224×224×3 image
- **DINOv2**: 256 patch tokens × 768 dimensions
- **Adapter**: 4 scales with total 16.3x feature expansion
- **Output**: Multi-scale pyramid ready for segmentation

### Computational Profile:
- **Trainable parameters**: ~50M (adapter only)
- **Memory efficient**: Frozen backbone + checkpointing
- **Inference speed**: Optimized for production use

## 🔬 Development History

All development files, alternative approaches, and debugging tools have been moved to `debugging_and_examples/` for reference. See `debugging_and_examples/README.md` for detailed information about:

- Alternative implementation approaches
- Comprehensive debugging tools  
- Size compatibility guides
- Feature visualization utilities
- Development learnings and solutions

## 📄 Citation

If you use this integration in your research, please cite both DINOv2 and DINOv3:

```bibtex
@article{dinov2,
  title={DINOv2: Learning Robust Visual Features without Supervision},
  author={Oquab, Maxime and Darcet, Timothée and others},
  journal={arXiv preprint arXiv:2304.07193},
  year={2023}
}

@article{dinov3,
  title={DINOv3: Learning Robust Visual Features without Supervision},
  author={Oquab, Maxime and Darcet, Timothée and others},
  journal={arXiv preprint arXiv:2508.10104},
  year={2024}
}
``` # m2f_vit_adapter
