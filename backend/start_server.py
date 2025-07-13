#!/usr/bin/env python3
"""
Startup script for the Enhanced Wildlife Audio Classification System
"""

import sys
import os
import traceback

def main():
    print("🚀 Starting Enhanced Wildlife Audio Classification System...")
    print("=" * 60)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from feature_extraction import AudioPreprocessor
        from model_manager import ModelLoader, AudioClassifier
        from database_manager import AudioDetectionDB
        from live_audio_recorder import LiveAudioRecorder
        print("✅ All imports successful!")
        
        # Test model loading
        print("🤖 Testing model loading...")
        model_loader = ModelLoader()
        audio_classifier = AudioClassifier(model_loader)
        print("✅ Models loaded successfully!")
        
        # Test database
        print("💾 Testing database...")
        database = AudioDetectionDB()
        print("✅ Database initialized successfully!")
        
        # Test audio preprocessor
        print("🎵 Testing audio preprocessor...")
        audio_preprocessor = AudioPreprocessor(target_sr=22050, target_duration=30)
        print("✅ Audio preprocessor initialized successfully!")
        
        print("\n🎉 All components tested successfully!")
        print("🚀 Starting FastAPI server...")
        
        # Import and run the FastAPI server
        import uvicorn
        from main import app
        
        print("🌐 Server starting on http://localhost:8000")
        print("📊 API docs available at: http://localhost:8000/docs")
        print("🔗 WebSocket endpoint: ws://localhost:8000/ws")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
