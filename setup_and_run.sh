#!/bin/bash
# Setup script: loads env, compiles deformable attention, runs training

set -e  # Exit on error

echo "========================================"
echo "🚀 SETUP AND RUN SCRIPT"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Load environment variables
echo ""
echo "📦 Step 1: Loading environment variables..."
if [ -f "env.sh" ]; then
    source env.sh
    echo "   ✅ env.sh loaded (HF_TOKEN set)"
else
    echo "   ⚠️  env.sh not found - make sure HF_TOKEN is set!"
fi

# Step 2: Compile deformable attention CUDA ops
echo ""
echo "🔧 Step 2: Compiling deformable attention CUDA ops..."
cd models/utils/ops

if [ -f "MultiScaleDeformableAttention.cpython-310-x86_64-linux-gnu.so" ]; then
    echo "   ℹ️  .so file already exists, recompiling anyway..."
fi

# Clean previous build
rm -rf build/ *.so *.egg-info 2>/dev/null || true

# Compile
python setup.py build_ext --inplace

if [ $? -eq 0 ]; then
    echo "   ✅ Deformable attention compiled successfully!"
    ls -la *.so 2>/dev/null || echo "   ⚠️  No .so file found"
else
    echo "   ❌ Compilation failed! Falling back to PyTorch implementation."
fi

cd "$SCRIPT_DIR"

# Step 3: Run training with 0 epochs (just to see logs)
echo ""
echo "🏋️ Step 3: Running training with 0 epochs (log test)..."
echo "========================================"
echo ""

python train_hydra.py training.max_epochs=0 "$@"

echo ""
echo "========================================"
echo "✅ Setup and test run complete!"
echo "========================================"
