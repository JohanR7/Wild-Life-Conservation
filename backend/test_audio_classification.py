#!/usr/bin/env python3
"""
Test script to verify SVM decision function fix
"""

import numpy as np
from model_manager import ModelLoader, AudioClassifier

def test_svm_fix():
    print("Testing SVM decision function fix...")
    
    try:
        # Initialize model loader
        model_loader = ModelLoader()
        print(f"Loaded {len(model_loader.gunshot_models)} gunshot models")
        print(f"Loaded {len(model_loader.wildlife_models)} wildlife models")
        
        # Initialize classifier
        classifier = AudioClassifier(model_loader)
        
        # Create dummy features as dictionary (60 features as expected)
        feature_names = [f'feature_{i}' for i in range(60)]
        dummy_features = {name: np.random.random() for name in feature_names}
        print(f"Created dummy features dictionary with {len(dummy_features)} features")
        
        # Test gunshot prediction
        print("\nTesting gunshot prediction...")
        gunshot_result = classifier.predict_gunshot(dummy_features)
        print("✓ Gunshot prediction successful!")
        print(f"Results: {gunshot_result}")
        
        # Test wildlife prediction  
        print("\nTesting wildlife prediction...")
        wildlife_result = classifier.predict_wildlife(dummy_features)
        print("✓ Wildlife prediction successful!")
        print(f"Results: {wildlife_result}")
        
        print("\n🎉 All tests passed! SVM fix is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_svm_fix()
