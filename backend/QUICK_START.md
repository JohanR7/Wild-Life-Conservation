# 🎯 Enhanced Wildlife Audio Classification System

## 🚀 Quick Start Guide

### 1. **System Validation**
Before starting, validate that all components work:
```bash
python validate_system.py
```

### 2. **Start the Server**
```bash
python main.py
```
The server will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

### 3. **Access the Frontend**
```bash
cd ../frontend
npm install  # First time only
npm start
```
Frontend will be available at: http://localhost:3000

---

## 🎵 **Features**

### ✅ **Live Audio Recording**
- **30-second chunks**: Continuous processing
- **Real-time results**: WebSocket streaming
- **Audio visualization**: Live audio levels
- **Smart queuing**: Up to 5 concurrent chunks

### ✅ **File Upload Analysis**
- **Multiple formats**: WAV, MP3, FLAC, M4A, OGG
- **Drag & drop**: Easy file selection
- **Instant results**: Quick analysis
- **Detailed output**: Confidence scores, probabilities

### ✅ **Database Storage**
- **All detections**: Stored in SQLite database
- **Animal counting**: Smart filtering (excludes machinery, etc.)
- **Statistics**: 24-hour summaries
- **History**: Complete detection timeline

### ✅ **Real-time Communication**
- **WebSocket**: Live data streaming
- **Status updates**: Recording start/stop
- **Detection alerts**: Instant notifications
- **Audio levels**: Real-time monitoring

---

## 🔧 **API Endpoints**

### **File Upload**
```http
POST /upload/single
Content-Type: multipart/form-data
```

### **Live Recording Control**
```http
POST /live-recording/start    # Start 30-second chunk recording
POST /live-recording/stop     # Stop recording
GET  /live-recording/status   # Get current status
```

### **Database Queries**
```http
GET /detections/recent        # Recent detections
GET /detections/stats         # 24-hour statistics
GET /wildlife/counts          # Animal count summary
```

### **WebSocket**
```javascript
ws://localhost:8000/ws
```
Receives real-time:
- Detection results
- Recording status
- Audio levels
- System notifications

---

## 📊 **Database Schema**

### **Detections Table**
- `id`, `timestamp`, `detection_type`
- `prediction`, `confidence`, `model_name`
- `probabilities` (JSON), `audio_filename`
- `processing_time`, `is_live_recording`

### **Animal Counts Table**  
- `animal_name`, `count`, `last_detected`
- Smart filtering (excludes non-animals)

### **System Status Table**
- `timestamp`, `status_type`, `status_value`, `details`

---

## 🎯 **Models Used**

### **Gunshot Detection**
- **XGBoost Model**: High accuracy gunshot classification
- **4 Classes**: Silent, Gunshot, Other Sound, Noise

### **Wildlife Classification**
- **XGBoost (ESC-50)**: Environmental sound classification
- **50 Classes**: Animals, nature sounds, human activities
- **Smart Filtering**: Only counts actual animals

---

## 🛠 **System Requirements**

### **Python Dependencies**
- FastAPI 2.0+
- PyAudio (for live recording)
- scikit-learn, XGBoost
- LibROSA, torchaudio
- SQLite3 (built-in)

### **Frontend Dependencies**
- React 18+
- WebSocket support
- Modern browser

---

## 🎉 **Usage Examples**

### **Live Recording**
1. Start server: `python main.py`
2. Open frontend: http://localhost:3000
3. Go to "Live Recording" tab
4. Click "Start Recording"
5. View real-time results every 30 seconds

### **File Analysis**
1. Go to Dashboard
2. Drag & drop audio file
3. Wait for analysis (usually < 5 seconds)
4. View detailed results with confidence scores

### **View Detection History**
1. Go to "Detections" tab
2. Browse all past detections
3. Filter by gunshot/wildlife
4. View detailed probabilities and model info

---

## 🚨 **Troubleshooting**

### **Import Errors**
```bash
# Validate system first
python validate_system.py

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### **Audio Issues**
```bash
# Test PyAudio installation
python -c "import pyaudio; print('PyAudio OK')"

# Check available audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)}') for i in range(p.get_device_count())]"
```

### **Model Loading Issues**
```bash
# Check model files exist
ls ../../ml_models/gun_shots/
ls ../../ml_models/wildlife/

# Test model loading
python -c "from model_manager import ModelLoader; ml = ModelLoader(); print('Models loaded OK')"
```

---

## 📁 **File Structure**
```
backend/
├── main.py                 # FastAPI server with all endpoints
├── model_manager.py        # ML model management
├── feature_extraction.py   # Audio preprocessing
├── database_manager.py     # SQLite database management
├── live_audio_recorder.py  # Live recording system
├── validate_system.py      # System validation script
└── audio_detections.db     # SQLite database (auto-created)

frontend/
├── src/
│   ├── App.jsx            # Main React application
│   └── Pages/
│       └── Dashboard.jsx  # Enhanced dashboard with all features
└── package.json           # React dependencies
```

---

## 🎯 **Ready to Use!**

Your enhanced audio classification system is now complete with:
- ✅ Live recording (30-second chunks)
- ✅ File upload analysis
- ✅ Real-time WebSocket communication  
- ✅ SQLite database with animal counting
- ✅ Comprehensive web interface
- ✅ Realistic confidence scores
- ✅ Production-ready architecture

**Happy audio classification! 🎵🔊**
