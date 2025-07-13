#!/usr/bin/env python3
"""
Test script to verify that all dependencies and modules are working correctly.
Run this before starting the main server to diagnose any issues.
"""

import sys
import os

def test_basic_imports():
    """Test basic Python imports"""
    print("=" * 60)
    print("TESTING BASIC IMPORTS")
    print("=" * 60)
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn: {e}")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    try:
        import torchaudio
        print(f"✅ TorchAudio: {torchaudio.__version__}")
    except ImportError as e:
        print(f"❌ TorchAudio: {e}")
        return False
    
    try:
        import librosa
        print(f"✅ LibROSA: {librosa.version.version}")
    except ImportError as e:
        print(f"❌ LibROSA: {e}")
        return False
    
    try:
        import sklearn
        print(f"✅ Scikit-learn: {sklearn.__version__}")
    except ImportError as e:
        print(f"❌ Scikit-learn: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ Pandas: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False
    
    try:
        import lightgbm as lgb
        print(f"✅ LightGBM: {lgb.__version__}")
    except ImportError as e:
        print(f"❌ LightGBM: {e}")
        return False
    
    try:
        import xgboost as xgb
        print(f"✅ XGBoost: {xgb.__version__}")
    except ImportError as e:
        print(f"❌ XGBoost: {e}")
        return False
    
    return True

def test_custom_modules():
    """Test our custom modules"""
    print("\n" + "=" * 60)
    print("TESTING CUSTOM MODULES")
    print("=" * 60)
    
    try:
        from feature_extraction import AudioPreprocessor, extract_features_enhanced
        print("✅ Feature extraction module imported successfully")
        
        # Test AudioPreprocessor instantiation
        preprocessor = AudioPreprocessor()
        print("✅ AudioPreprocessor instantiated successfully")
    except ImportError as e:
        print(f"❌ Feature extraction module: {e}")
        return False
    except Exception as e:
        print(f"❌ Feature extraction error: {e}")
        return False
    
    try:
        from model_manager import ModelLoader, AudioClassifier
        print("✅ Model manager module imported successfully")
    except ImportError as e:
        print(f"❌ Model manager module: {e}")
        return False
    except Exception as e:
        print(f"❌ Model manager error: {e}")
        return False
    
    return True

def test_model_loading():
    """Test model loading"""
    print("\n" + "=" * 60)
    print("TESTING MODEL LOADING")
    print("=" * 60)
    
    try:
        from model_manager import ModelLoader, AudioClassifier
        
        # Check if models directory exists
        models_path = "../ml_models"
        if not os.path.exists(models_path):
            print(f"❌ Models directory not found: {models_path}")
            print("   Please ensure your trained models are in the correct location.")
            return False
        
        print(f"✅ Models directory found: {models_path}")
        
        # Try to load models
        model_loader = ModelLoader(models_path)
        print(f"✅ ModelLoader instantiated")
        print(f"   Gunshot models: {len(model_loader.gunshot_models)}")
        print(f"   Wildlife models: {len(model_loader.wildlife_models)}")
        print(f"   Scalers: {len(model_loader.scalers)}")
        
        if len(model_loader.gunshot_models) == 0 and len(model_loader.wildlife_models) == 0:
            print("⚠️  No models loaded. Check your model files.")
            return False
        
        # Try to instantiate classifier
        classifier = AudioClassifier(model_loader)
        print("✅ AudioClassifier instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        return False

def test_audio_processing():
    """Test basic audio processing"""
    print("\n" + "=" * 60)
    print("TESTING AUDIO PROCESSING")
    print("=" * 60)
    
    try:
        import torch
        import torchaudio
        import librosa
        import numpy as np
        
        # Create a simple test audio signal
        sample_rate = 22050
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_signal = np.sin(2 * np.pi * frequency * t)
        
        # Test torch audio processing
        waveform = torch.tensor(test_signal).unsqueeze(0).float()
        print(f"✅ Test signal created: shape {waveform.shape}")
        
        # Test MFCC extraction
        mfcc_transform = torchaudio.transforms.MFCC(sample_rate=sample_rate, n_mfcc=13)
        mfccs = mfcc_transform(waveform)
        print(f"✅ MFCC extraction: shape {mfccs.shape}")
        
        # Test librosa features
        chroma = librosa.feature.chroma_stft(y=test_signal, sr=sample_rate)
        print(f"✅ Chroma extraction: shape {chroma.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processing error: {e}")
        return False

def main():
    """Run all tests"""
    print("AUDIO CLASSIFICATION MIDDLEWARE - DEPENDENCY TEST")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Virtual environment: {'venv' in sys.executable}")
    
    all_passed = True
    
    # Run tests
    if not test_basic_imports():
        all_passed = False
    
    if not test_custom_modules():
        all_passed = False
    
    if not test_model_loading():
        all_passed = False
    
    if not test_audio_processing():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! You can now start the server.")
        print("\nTo start the server:")
        print("  1. Run: quick_start.bat")
        print("  2. Or run: python main.py (make sure virtual environment is active)")
    else:
        print("❌ SOME TESTS FAILED. Please fix the issues above before starting the server.")
        print("\nCommon solutions:")
        print("  1. Make sure you're in the virtual environment")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. Check that all model files are in ../ml_models/")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
