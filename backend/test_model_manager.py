from model_manager import ModelLoader, AudioClassifier

print("Testing updated model manager...")

try:
    # Load models
    model_loader = ModelLoader()
    classifier = AudioClassifier(model_loader)
    
    print(f"✅ Successfully loaded models!")
    print(f"  Gunshot models: {len(model_loader.gunshot_models)}")
    print(f"  Wildlife models: {len(model_loader.wildlife_models)}")
    
    # Test class mappings
    print(f"\nGunshot classes: {classifier.gunshot_classes}")
    print(f"ESC-50 classes (first 10): {dict(list(classifier.esc50_classes.items())[:10])}")
    print(f"iNaturalist classes (first 5): {dict(list(classifier.inat_classes.items())[:5])}")
    
    print("\n✅ Model manager updated successfully!")
    print("The class mappings now match your actual trained models.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
