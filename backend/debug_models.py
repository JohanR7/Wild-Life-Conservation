from pathlib import Path
import joblib

# Check model loading with detailed debugging
base_path = Path("../../ml_models")
print(f"Checking model path: {base_path.absolute()}")

# Check gunshot models
gunshot_path = base_path / "gun_shots"
print(f"\nGunshot path: {gunshot_path.absolute()}")
print(f"Gunshot path exists: {gunshot_path.exists()}")
if gunshot_path.exists():
    files = list(gunshot_path.glob("*.pkl"))
    print(f"PKL files found: {[f.name for f in files]}")
    
    for file in files:
        if "scaler" not in file.name:
            try:
                print(f"Trying to load: {file.name}")
                model = joblib.load(file)
                print(f"  ✅ Loaded successfully: {type(model)}")
            except Exception as e:
                print(f"  ❌ Failed to load: {e}")

# Check wildlife models  
wildlife_path = base_path / "wildlife"
print(f"\nWildlife path: {wildlife_path.absolute()}")
print(f"Wildlife path exists: {wildlife_path.exists()}")
if wildlife_path.exists():
    files = list(wildlife_path.glob("*.pkl"))
    print(f"PKL files found: {[f.name for f in files]}")
    
    for file in files:
        try:
            print(f"Trying to load: {file.name}")
            model = joblib.load(file)
            print(f"  ✅ Loaded successfully: {type(model)}")
        except Exception as e:
            print(f"  ❌ Failed to load: {e}")
            print(f"      Error details: {str(e)[:100]}")
