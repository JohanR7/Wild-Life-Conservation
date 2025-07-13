import logging
logging.basicConfig(level=logging.INFO)

from model_manager import ModelLoader, AudioClassifier

print("Testing model loading with debug info...")

try:
    # Load models with debug
    model_loader = ModelLoader()
    classifier = AudioClassifier(model_loader)
    
    print(f"Models loaded:")
    print(f"  Gunshot models: {list(model_loader.gunshot_models.keys())}")
    print(f"  Wildlife models: {list(model_loader.wildlife_models.keys())}")
    print(f"  Scalers: {list(model_loader.scalers.keys())}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
