import tempfile
import numpy as np
import soundfile as sf
from feature_extraction import AudioPreprocessor

# Create a simple test audio
duration = 3  # seconds
sr = 22050
t = np.linspace(0, duration, int(sr * duration))
test_audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

# Save to temp file and extract features
with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
    sf.write(tmp.name, test_audio, sr)
    
    processor = AudioPreprocessor()
    features = processor.extract_features_enhanced(tmp.name)
    
    if features:
        actual_count = len(features)
        expected_count = processor.get_feature_count()
        
        print(f"Expected features: {expected_count}")
        print(f"Actual features extracted: {actual_count}")
        
        if actual_count == expected_count == 60:
            print("🎯 PERFECT! Both match 60 features")
        elif actual_count == expected_count:
            print(f"✅ Consistent but wrong count: {actual_count}")
        else:
            print(f"❌ MISMATCH! Expected {expected_count}, got {actual_count}")
            
        # Show first few actual feature names
        actual_names = list(features.keys())[:10]
        print(f"First 10 actual features: {actual_names}")
        
        if actual_count != 60:
            print(f"Need to remove {actual_count - 60} more features")
    else:
        print("❌ Feature extraction failed")

import os
os.unlink(tmp.name)
