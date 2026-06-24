import os
import shutil
import random
from pathlib import Path

# Configuration
SOURCE_DIR = 'data/train'  # Source directory with all images per class
TRAIN_DIR = 'data/train_split'  # Destination for training split
VAL_DIR = 'data/val_split'      # Destination for validation split
SPLIT_RATIO = 0.2        # 20% for validation
SEED = 42

random.seed(SEED)

def split_class_dir(source_class_dir, train_out, val_out, split_ratio):
    """Split images from source class directory into train and val."""
    images = [f for f in os.listdir(source_class_dir) if os.path.isfile(os.path.join(source_class_dir, f))]
    
    if not images:
        return 0, 0
    
    random.shuffle(images)
    n_val = int(len(images) * split_ratio)
    val_images = images[:n_val]
    train_images = images[n_val:]

    # Copy images to train
    for img in train_images:
        shutil.copy2(os.path.join(source_class_dir, img), os.path.join(train_out, img))
    
    # Copy images to val
    for img in val_images:
        shutil.copy2(os.path.join(source_class_dir, img), os.path.join(val_out, img))
    
    return len(train_images), len(val_images)


def main():
    """Split dataset into train and val sets."""
    print("Starting dataset split...")
    print(f"Source: {SOURCE_DIR}")
    print(f"Train output: {TRAIN_DIR}")
    print(f"Val output: {VAL_DIR}")
    print(f"Split ratio: {SPLIT_RATIO} (validation)")
    
    # Clean/create output dirs
    for split_dir in [TRAIN_DIR, VAL_DIR]:
        if os.path.exists(split_dir):
            shutil.rmtree(split_dir)
        os.makedirs(split_dir, exist_ok=True)

    # Get all class directories
    class_dirs = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
    
    if not class_dirs:
        print(f"ERROR: No class directories found in {SOURCE_DIR}")
        return
    
    total_train = 0
    total_val = 0
    
    # Split each class
    for class_name in class_dirs:
        source_path = os.path.join(SOURCE_DIR, class_name)
        train_out = os.path.join(TRAIN_DIR, class_name)
        val_out = os.path.join(VAL_DIR, class_name)
        
        # Create class output dirs
        os.makedirs(train_out, exist_ok=True)
        os.makedirs(val_out, exist_ok=True)
        
        # Split this class
        n_train, n_val = split_class_dir(source_path, train_out, val_out, SPLIT_RATIO)
        total_train += n_train
        total_val += n_val
        
        print(f"✓ {class_name}: {n_train} train, {n_val} val")

    print(f"\n✅ Dataset split complete!")
    print(f"Total training images: {total_train}")
    print(f"Total validation images: {total_val}")

if __name__ == "__main__":
    main()
