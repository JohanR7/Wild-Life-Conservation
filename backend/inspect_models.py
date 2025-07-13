import joblib
from pathlib import Path

def inspect_model(model_path):
    """Inspect a pickle model to extract class information"""
    print(f"\n{'='*60}")
    print(f"Inspecting: {model_path}")
    print(f"{'='*60}")
    
    try:
        model = joblib.load(model_path)
        print(f"Model type: {type(model)}")
        
        # Check for classes_ attribute (common in sklearn models)
        if hasattr(model, 'classes_'):
            print(f"Classes: {model.classes_}")
            print(f"Number of classes: {len(model.classes_)}")
            
            # Create class mapping
            class_mapping = {i: str(cls) for i, cls in enumerate(model.classes_)}
            print(f"Class mapping: {class_mapping}")
        
        # Check for other common attributes
        if hasattr(model, 'feature_names_in_'):
            print(f"Feature names: {model.feature_names_in_[:10]}...")  # Show first 10
            print(f"Number of features: {len(model.feature_names_in_)}")
        
        if hasattr(model, 'n_features_in_'):
            print(f"Number of input features: {model.n_features_in_}")
            
        if hasattr(model, 'n_classes_'):
            print(f"Number of classes: {model.n_classes_}")
            
        # For tree-based models, check feature importances
        if hasattr(model, 'feature_importances_'):
            print(f"Has feature importances: True")
            
        # For XGBoost models
        if hasattr(model, 'objective'):
            print(f"Objective: {model.objective}")
            
        # For LightGBM models
        if hasattr(model, 'params'):
            print(f"Params: {model.params}")
            
        # Try to get more info about the model
        print(f"\nAll attributes:")
        attrs = [attr for attr in dir(model) if not attr.startswith('_')]
        for attr in attrs[:20]:  # Show first 20 attributes
            try:
                value = getattr(model, attr)
                if not callable(value):
                    print(f"  {attr}: {type(value)} - {str(value)[:100]}")
            except:
                pass
                
        return model
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def inspect_all_models():
    """Inspect all models in the ml_models directory"""
    base_path = Path("../../ml_models")
    
    print("GUNSHOT MODELS")
    print("="*80)
    
    gunshot_path = base_path / "gun_shots"
    if gunshot_path.exists():
        for model_file in gunshot_path.glob("*.pkl"):
            inspect_model(model_file)
    
    print("\n\nWILDLIFE MODELS")
    print("="*80)
    
    wildlife_path = base_path / "wildlife"
    if wildlife_path.exists():
        for model_file in wildlife_path.glob("*.pkl"):
            inspect_model(model_file)

def create_class_mappings():
    """Create the correct class mappings based on model inspection"""
    print("\n\n" + "="*80)
    print("GENERATING CLASS MAPPINGS FOR model_manager.py")
    print("="*80)
    
    base_path = Path("../../ml_models")
    
    # Dictionary to store class mappings
    gunshot_mapping = None
    wildlife_mappings = {}
    
    # Check gunshot models
    gunshot_path = base_path / "gun_shots"
    if gunshot_path.exists():
        for model_file in gunshot_path.glob("*.pkl"):
            if "scaler" not in model_file.name:
                try:
                    model = joblib.load(model_file)
                    if hasattr(model, 'classes_'):
                        gunshot_mapping = {i: str(cls) for i, cls in enumerate(model.classes_)}
                        print(f"\nGunshot classes from {model_file.name}:")
                        print(f"self.gunshot_classes = {gunshot_mapping}")
                        break
                except:
                    continue
    
    # Check wildlife models
    wildlife_path = base_path / "wildlife"
    if wildlife_path.exists():
        for model_file in wildlife_path.glob("*.pkl"):
            try:
                model = joblib.load(model_file)
                if hasattr(model, 'classes_'):
                    mapping = {i: str(cls) for i, cls in enumerate(model.classes_)}
                    wildlife_mappings[model_file.stem] = mapping
                    print(f"\nWildlife classes from {model_file.name}:")
                    print(f"{model_file.stem}_classes = {mapping}")
            except:
                continue
    
    # Generate unified wildlife mapping if they're consistent
    if wildlife_mappings:
        # Check if all wildlife models have the same classes
        all_classes = list(wildlife_mappings.values())
        if len(set(str(mapping) for mapping in all_classes)) == 1:
            print(f"\n✅ All wildlife models have consistent classes:")
            print(f"self.wildlife_classes = {all_classes[0]}")
        else:
            print(f"\n⚠️ Wildlife models have different classes:")
            for model_name, mapping in wildlife_mappings.items():
                print(f"  {model_name}: {mapping}")

if __name__ == "__main__":
    inspect_all_models()
    create_class_mappings()
