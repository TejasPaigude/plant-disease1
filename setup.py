"""
Setup script to initialize the Plant Disease Detection project.
Generates placeholder files and directories if they don't exist.
"""

import os
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_directory_structure():
    """Create all required directories."""
    directories = [
        'models',
        'assets/demo',
        'data/train',
        'data/val',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_demo_image():
    """Create a placeholder demo image."""
    demo_path = Path('assets/demo/sample_leaf.jpg')
    
    if demo_path.exists():
        print("✓ Demo image already exists")
        return
    
    # Create a simple leaf-like image
    width, height = 224, 224
    img = Image.new('RGB', (width, height), color=(34, 139, 34))  # Forest green
    draw = ImageDraw.Draw(img)
    
    # Draw leaf shape
    leaf_points = [
        (112, 30),   # Top point
        (180, 80),   # Right upper
        (160, 112),  # Right middle
        (190, 150),  # Right lower
        (112, 190),  # Bottom point
        (34, 150),   # Left lower
        (64, 112),   # Left middle
        (44, 80),    # Left upper
    ]
    
    # Draw filled polygon (leaf shape)
    draw.polygon(leaf_points, fill=(50, 205, 50), outline=(34, 139, 34))
    
    # Add vein details
    draw.line([(112, 30), (112, 190)], fill=(34, 139, 34), width=2)
    for x, y in leaf_points[1::2]:
        draw.line([(112, 110), (x, y)], fill=(34, 139, 34), width=1)
    
    # Add text
    try:
        draw.text((45, 200), "Healthy Leaf", fill=(255, 255, 255))
    except:
        pass  # Font might not be available
    
    # Save image
    img.save(demo_path)
    print(f"✓ Created demo image: {demo_path}")

def create_labels_file():
    """Verify labels.json exists or create a minimal version."""
    labels_path = Path('labels.json')
    
    if labels_path.exists():
        print("✓ labels.json already exists")
        return
    
    # Create minimal labels
    minimal_labels = {
        "Apple___healthy": {
            "display": "Apple - Healthy",
            "remedy": "No treatment needed."
        },
        "Tomato___healthy": {
            "display": "Tomato - Healthy",
            "remedy": "No treatment needed."
        },
    }
    
    with open(labels_path, 'w') as f:
        json.dump(minimal_labels, f, indent=4)
    
    print(f"✓ Created labels.json")

def create_sample_data_classes():
    """Create sample class folders in data directories."""
    sample_classes = ['Apple___healthy', 'Tomato___healthy', 'Potato___Early_blight']
    
    for data_type in ['train', 'val']:
        for class_name in sample_classes:
            class_path = Path(f'data/{data_type}/{class_name}')
            class_path.mkdir(parents=True, exist_ok=True)
    
    print("✓ Created sample data class folders")

def create_requirements_check():
    """Check and display requirements."""
    requirements_file = Path('requirements.txt')
    
    if requirements_file.exists():
        print("\n✓ requirements.txt exists")
        print("\nTo install dependencies, run:")
        print("  pip install -r requirements.txt")
    else:
        print("\n⚠ requirements.txt not found")

def print_next_steps():
    """Print setup complete message with next steps."""
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\n📝 Next Steps:")
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. (Optional) Train the model:")
    print("   - Download PlantVillage dataset from Kaggle")
    print("   - Extract to data/train and data/val")
    print("   - Run: python model_training.py")
    print("\n3. Run the Streamlit app:")
    print("   streamlit run app.py")
    print("\n4. Open browser to:")
    print("   http://localhost:8501")
    print("\n5. Try the demo image or upload your own!")
    print("\n" + "="*60)

def main():
    """Run all setup tasks."""
    print("\n🌾 Plant Disease Detection - Setup")
    print("="*60)
    
    try:
        print("\n📁 Creating directory structure...")
        create_directory_structure()
        
        print("\n🖼️  Creating demo image...")
        create_demo_image()
        
        print("\n📋 Setting up labels...")
        create_labels_file()
        
        print("\n📂 Creating sample data folders...")
        create_sample_data_classes()
        
        print("\n✅ Checking requirements...")
        create_requirements_check()
        
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
