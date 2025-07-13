#!/usr/bin/env python3
"""
Debug SVM decision function issue
"""

import numpy as np
from model_manager import ModelLoader

def debug_svm():
    print("Loading models...")
    loader = ModelLoader()
    
    print(f"Available gunshot models: {list(loader.gunshot_models.keys())}")
    
    if 'svm' in loader.gunshot_models:
        svm = loader.gunshot_models['svm']
        print(f"SVM model type: {type(svm)}")
        
        # Test with random features
        test_features = np.random.random((1, 60))
        print(f"Test features shape: {test_features.shape}")
        
        print("Testing decision_function...")
        try:
            decision = svm.decision_function(test_features)
            print(f"Decision result: {decision}")
            print(f"Decision shape: {decision.shape}")
            print(f"Decision type: {type(decision)}")
            print(f"Decision size: {decision.size}")
            print(f"Decision ndim: {decision.ndim}")
            
            # Try to convert to float
            print("Testing float conversion...")
            if decision.shape == ():
                val = decision.item()
                print(f"Using .item(): {val}, type: {type(val)}")
            elif decision.size == 1:
                val = decision.flatten()[0]
                print(f"Using .flatten()[0]: {val}, type: {type(val)}")
            else:
                val = decision[0]
                print(f"Using [0]: {val}, type: {type(val)}")
            
            final_val = float(val)
            print(f"Final float value: {final_val}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No SVM model found")

if __name__ == "__main__":
    debug_svm()
