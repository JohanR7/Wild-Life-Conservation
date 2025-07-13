import joblib
from pathlib import Path

# Load one model from each type to check the actual class count
base_path = Path("../../ml_models")

print("ACTUAL MODEL CLASS INFORMATION:")
print("="*50)

# Check gunshot models
gunshot_path = base_path / "gun_shots"
if gunshot_path.exists():
    svm_path = gunshot_path / "svm_model.pkl"
    if svm_path.exists():
        try:
            model = joblib.load(svm_path)
            print(f"\nGunshot SVM Model:")
            print(f"  Classes: {model.classes_}")
            print(f"  Number of classes: {len(model.classes_)}")
        except Exception as e:
            print(f"  Error loading SVM: {e}")

# Check wildlife models - ESC-50
wildlife_path = base_path / "wildlife"
if wildlife_path.exists():
    esc50_path = wildlife_path / "rf_model_esc50.pkl"
    if esc50_path.exists():
        try:
            model = joblib.load(esc50_path)
            print(f"\nWildlife ESC-50 Model:")
            print(f"  Classes: {model.classes_}")
            print(f"  Number of classes: {len(model.classes_)}")
        except Exception as e:
            print(f"  Error loading ESC-50: {e}")
    
    # Check iNaturalist model
    inat_path = wildlife_path / "lightgbm_inat_overfitting.pkl"
    if inat_path.exists():
        try:
            model = joblib.load(inat_path)
            print(f"\nWildlife iNaturalist Model:")
            print(f"  Classes: {model.classes_[:10]}... (showing first 10)")
            print(f"  Number of classes: {len(model.classes_)}")
        except Exception as e:
            print(f"  Error loading iNaturalist: {e}")

print("\nCONCLUSION:")
print("Your models have these class structures:")
print("- Gunshot models: 4 classes (likely: quiet, gunshot, other_sound, noise)")
print("- ESC-50 models: 50 classes (environmental sound dataset)")
print("- iNaturalist models: ~400 classes (species identification)")
print("\nWe need to update the class mappings in model_manager.py!")
