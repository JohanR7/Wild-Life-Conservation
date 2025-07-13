"""
Quick system validation script to verify all components work together
"""

def test_system():
    print("🧪 Testing Enhanced Audio Classification System")
    print("=" * 60)
    
    errors = []
    
    # Test 1: Import all modules
    try:
        print("📦 Testing imports...")
        from feature_extraction import AudioPreprocessor
        from model_manager import ModelLoader, AudioClassifier
        from database_manager import AudioDetectionDB
        from live_audio_recorder import LiveAudioRecorder
        print("✅ All imports successful!")
    except Exception as e:
        errors.append(f"Import error: {e}")
        print(f"❌ Import failed: {e}")
    
    # Test 2: Model initialization
    try:
        print("🤖 Testing model initialization...")
        model_loader = ModelLoader()
        print(f"✅ Loaded gunshot models: {list(model_loader.gunshot_models.keys())}")
        print(f"✅ Loaded wildlife models: {list(model_loader.wildlife_models.keys())}")
        
        audio_classifier = AudioClassifier(model_loader)
        print("✅ AudioClassifier initialized!")
    except Exception as e:
        errors.append(f"Model initialization error: {e}")
        print(f"❌ Model initialization failed: {e}")
    
    # Test 3: Database connection
    try:
        print("💾 Testing database...")
        db = AudioDetectionDB()
        stats = db.get_detection_stats()
        print(f"✅ Database connected! Current detections: {stats['total_detections']}")
    except Exception as e:
        errors.append(f"Database error: {e}")
        print(f"❌ Database failed: {e}")
    
    # Test 4: Audio preprocessor
    try:
        print("🎵 Testing audio preprocessor...")
        preprocessor = AudioPreprocessor(target_sr=22050, target_duration=30)
        print("✅ AudioPreprocessor initialized!")
    except Exception as e:
        errors.append(f"Audio preprocessor error: {e}")
        print(f"❌ Audio preprocessor failed: {e}")
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 40)
    if not errors:
        print("🎉 All tests passed! System is ready!")
        print("\n🚀 To start the server:")
        print("   python main.py")
        print("\n📊 Server will be available at:")
        print("   http://localhost:8000")
        print("   http://localhost:8000/docs (API documentation)")
        return True
    else:
        print(f"❌ {len(errors)} errors found:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        return False

if __name__ == "__main__":
    test_system()
