import os
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader


def collate_fn(batch):
    """
    Custom collate function to handle batches of data with varying numbers of masks.

    This function takes a list of dictionaries (one for each sample in the batch)
    and combines them into a single dictionary for the model.
    """
    pixel_values = torch.stack([item["pixel_values"] for item in batch])
    mask_labels = [item["mask_labels"] for item in batch]
    class_labels = [item["class_labels"] for item in batch]
    return {
        "pixel_values": pixel_values,
        "mask_labels": mask_labels,
        "class_labels": class_labels,
    }


class LoveDADataset(Dataset):
    """
    Custom PyTorch Dataset for the LoveDA dataset.

    This dataset class is designed to handle the specific folder structure
    of LoveDA, which is split into 'Urban' and 'Rural' sub-directories.
    """
    def __init__(self, split_dir, processor, transform=None):
        """
        Args:
            split_dir (str): Path to the directory for the split (e.g., '.../LoveDA/Train').
            processor: The Hugging Face AutoImageProcessor for Mask2Former.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.processor = processor
        self.transform = transform

        self.image_paths = []
        self.mask_paths = []

        # The dataset is divided into 'Rural' and 'Urban' scenes.
        # We need to gather images and masks from both.
        for scene_type in ["Rural", "Urban"]:
            scene_path = os.path.join(split_dir, scene_type)
            if os.path.isdir(scene_path):
                image_dir = os.path.join(scene_path, "images_png")
                mask_dir = os.path.join(scene_path, "masks_png")

                if not os.path.isdir(image_dir):
                    continue

                image_filenames = sorted(os.listdir(image_dir))

                for filename in image_filenames:
                    if filename.endswith(".png"):
                        self.image_paths.append(os.path.join(image_dir, filename))
                        self.mask_paths.append(os.path.join(mask_dir, filename))

        assert len(self.image_paths) == len(self.mask_paths), "Mismatch between number of images and masks."

        if len(self.image_paths) == 0:
            print(f"WARNING: No images found in {split_dir}. Check your path and dataset structure.")
        else:
            print(f"Found {len(self.image_paths)} images in {split_dir}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        mask = Image.open(self.mask_paths[idx]).convert("L")

        # Apply any additional custom transforms if provided
        if self.transform:
            image = self.transform(image)

        # Process with Hugging Face processor
        inputs = self.processor(
            images=image,
            segmentation_maps=mask,
            return_tensors="pt"
        )

        return {
            "pixel_values": inputs["pixel_values"].squeeze(0),
            "mask_labels": inputs["mask_labels"][0],
            "class_labels": inputs["class_labels"][0]
        }


def create_dataloaders(data_dir, processor, batch_size=4, num_workers=4):
    """
    Create train, validation, and test DataLoaders for the LoveDA dataset.

    Args:
        data_dir (str): Root directory of the LoveDA dataset (contains Train/, Val/, Test/).
        processor: The Hugging Face AutoImageProcessor for Mask2Former.
        batch_size (int): Batch size for all DataLoaders.
        num_workers (int): Number of parallel data loading workers.

    Returns:
        Tuple of (train_loader, val_loader, test_loader).
        test_loader is None if the Test split is missing or empty.
    """
    train_dir = os.path.join(data_dir, "Train")
    val_dir = os.path.join(data_dir, "Val")
    test_dir = os.path.join(data_dir, "Test")

    train_dataset = LoveDADataset(train_dir, processor)
    val_dataset = LoveDADataset(val_dir, processor)

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, collate_fn=collate_fn, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, collate_fn=collate_fn, pin_memory=True
    )

    # Test split may not have masks — create loader only if directory exists and has samples
    test_loader = None
    if os.path.isdir(test_dir):
        test_dataset = LoveDADataset(test_dir, processor)
        if len(test_dataset) > 0:
            test_loader = DataLoader(
                test_dataset, batch_size=batch_size, shuffle=False,
                num_workers=num_workers, collate_fn=collate_fn, pin_memory=True
            )

    return train_loader, val_loader, test_loader
