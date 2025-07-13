import joblib
from pathlib import Path

def check_model_classes():
    """Quick check for model classes"""
    base_path = Path("../../ml_models")
    
    print("CHECKING MODEL CLASSES...")
    print("="*50)
    
    # Check gunshot models
    gunshot_path = base_path / "gun_shots"
    print(f"\nGUNSHOT MODELS in {gunshot_path}:")
    if gunshot_path.exists():
        for model_file in gunshot_path.glob("*.pkl"):
            if "scaler" not in model_file.name:
                try:
                    print(f"\nLoading: {model_file.name}")
                    model = joblib.load(model_file)
                    if hasattr(model, 'classes_'):
                        print(f"  Classes: {model.classes_}")
                        print(f"  Class mapping: {dict(enumerate(model.classes_))}")
                    else:
                        print(f"  No classes_ attribute found")
                        print(f"  Model type: {type(model)}")
                except Exception as e:
                    print(f"  Error: {e}")
    
    # Check wildlife models  
    wildlife_path = base_path / "wildlife"
    print(f"\nWILDLIFE MODELS in {wildlife_path}:")
    if wildlife_path.exists():
        for model_file in wildlife_path.glob("*.pkl"):
            try:
                print(f"\nLoading: {model_file.name}")
                model = joblib.load(model_file)
                if hasattr(model, 'classes_'):
                    print(f"  Classes: {model.classes_}")
                    print(f"  Class mapping: {dict(enumerate(model.classes_))}")
                else:
                    print(f"  No classes_ attribute found")
                    print(f"  Model type: {type(model)}")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    check_model_classes()
