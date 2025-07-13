# Audio Classification Middleware

A FastAPI-based middleware service that can process up to 5 audio files simultaneously and classify them using your trained gunshot detection and wildlife classification models.

## Features

- **Concurrent Processing**: Handle up to 5 audio files simultaneously
- **Multiple Models**: Uses all available gunshot (SVM, XGBoost) and wildlife models (LightGBM, Random Forest, XGBoost variants)
- **Best Prediction Selection**: Automatically selects the prediction with the highest confidence score
- **Web Interface**: Simple HTML interface for testing
- **REST API**: RESTful endpoints for integration
- **WebSocket Support**: Real-time communication capabilities
- **Feature Extraction**: Enhanced audio feature extraction pipeline

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── feature_extraction.py   # Audio preprocessing and feature extraction
├── model_manager.py        # Model loading and prediction management
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── start_server.bat       # Windows startup script
├── test_interface.html    # Web testing interface
└── README.md             # This file
```

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Your trained models in `../ml_models/` directory:
  ```
  ml_models/
  ├── gun_shots/
  │   ├── scaler.pkl
  │   ├── svm_model.pkl
  │   └── xgboost_model.pkl
  └── wildlife/
      ├── lightgbm_inat_overfitting.pkl
      ├── rf_model_esc50.pkl
      ├── xgboost_inat_overfitting.pkl
      └── xgboost_model_esc50.pkl
  ```

### 2. Installation & Startup

#### Option A: Using the Batch Script (Windows)
```bash
# Simply double-click start_server.bat or run:
start_server.bat
```

#### Option B: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

### 3. Testing

1. **Web Interface**: Open `test_interface.html` in your browser
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Health Check**: Visit http://localhost:8000/health

## API Endpoints

### Upload Multiple Files
```http
POST /upload_audio
Content-Type: multipart/form-data

# Upload up to 5 audio files
# Returns predictions from all models with best overall prediction
```

### Upload Single File
```http
POST /classify_single
Content-Type: multipart/form-data

# Upload and classify a single audio file
```

### Health Check
```http
GET /health

# Returns server status and loaded models count
```

### Models Information
```http
GET /models/info

# Returns detailed information about loaded models
```

### WebSocket
```http
WS /ws

# Real-time communication endpoint
# Supports audio streaming and live predictions
```

## Usage Examples

### Python Client Example
```python
import requests

# Upload multiple files
files = [
    ('files', open('audio1.wav', 'rb')),
    ('files', open('audio2.wav', 'rb')),
    ('files', open('audio3.wav', 'rb'))
]

response = requests.post('http://localhost:8000/upload_audio', files=files)
result = response.json()

# Get best prediction
best = result['best_overall_prediction']
print(f"Best prediction: {best['prediction']} with {best['confidence']:.2%} confidence")

# Close files
for _, file in files:
    file.close()
```

### JavaScript Client Example
```javascript
const formData = new FormData();
formData.append('files', audioFile1);
formData.append('files', audioFile2);

fetch('http://localhost:8000/upload_audio', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Best prediction:', data.best_overall_prediction);
    console.log('All results:', data.results);
});
```

## Response Format

```json
{
    "success": true,
    "total_files": 3,
    "results": [
        {
            "filename": "audio1.wav",
            "success": true,
            "classification": {
                "success": true,
                "gunshot_predictions": {
                    "svm": {
                        "prediction": "Gunshot",
                        "confidence": 0.85,
                        "probabilities": {"Non-Gunshot": 0.15, "Gunshot": 0.85},
                        "model_type": "gunshot"
                    },
                    "xgboost": {
                        "prediction": "Gunshot",
                        "confidence": 0.92,
                        "probabilities": {"Non-Gunshot": 0.08, "Gunshot": 0.92},
                        "model_type": "gunshot"
                    }
                },
                "wildlife_predictions": {
                    "lightgbm_inat": {
                        "prediction": "Class_0",
                        "confidence": 0.75,
                        "model_type": "wildlife"
                    }
                },
                "best_result": {
                    "best_prediction": "Gunshot",
                    "best_confidence": 0.92,
                    "best_model": "xgboost"
                }
            },
            "processing_time": 2.34,
            "feature_count": 67
        }
    ],
    "best_overall_prediction": {
        "filename": "audio1.wav",
        "prediction": "Gunshot",
        "confidence": 0.92,
        "model": "xgboost"
    },
    "processing_summary": {
        "total_processing_time": 6.78,
        "successful_files": 3,
        "failed_files": 0
    }
}
```

## Supported Audio Formats

- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)

## Configuration

Edit `config.py` to customize:

- Server host and port
- Maximum file size and count
- Audio processing parameters
- Model paths
- CORS settings

## Features

### Audio Preprocessing
- Automatic resampling to 22050 Hz
- Duration normalization (30 seconds)
- Silence removal
- Audio validation
- Noise filtering

### Feature Extraction
- 67 optimized features including:
  - MFCC coefficients (0-12) with mean/std
  - Delta and Delta-Delta MFCCs
  - Spectral features (centroid, bandwidth, rolloff, flatness)
  - Chroma features
  - Spectral contrast
  - Zero crossing rate
  - RMS energy with quantiles
  - Onset strength

### Model Management
- Automatic model discovery and loading
- Support for multiple model types (SVM, XGBoost, LightGBM, Random Forest)
- Graceful error handling for missing models
- Confidence-based best prediction selection

## Troubleshooting

### Common Issues

1. **Models not loading**
   - Ensure models are in the correct directory structure
   - Check file permissions
   - Verify model file integrity

2. **Audio processing errors**
   - Verify audio file format is supported
   - Check file is not corrupted
   - Ensure sufficient disk space

3. **Server won't start**
   - Check if port 8000 is available
   - Verify all dependencies are installed
   - Check Python version compatibility

### Logs

The server provides detailed logging. Check console output for:
- Model loading status
- Processing errors
- Performance metrics

## Performance

- **Concurrent Processing**: Up to 5 files simultaneously
- **Average Processing Time**: 2-5 seconds per file (depends on file size and hardware)
- **Memory Usage**: ~200-500MB (depends on model size)
- **CPU Usage**: Utilizes multiple cores for concurrent processing

## Development

### Adding New Models

1. Place model files in appropriate directories
2. Update class mappings in `model_manager.py`
3. Restart the server

### Extending Features

- Add new audio features in `feature_extraction.py`
- Implement custom preprocessing in `AudioPreprocessor`
- Add new endpoints in `main.py`

## Security Notes

- In production, configure CORS origins properly
- Implement authentication if needed
- Set appropriate file size limits
- Use HTTPS in production

## License

This project is part of the Wild Life Conservation system.
