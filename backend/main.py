from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import tempfile
import os
import logging
from typing import List, Dict, Optional
import json
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime
from pathlib import Path

# Import our custom modules
try:
    from feature_extraction import AudioPreprocessor
    from model_manager import ModelLoader, AudioClassifier
    from database_manager import AudioDetectionDB
    from live_audio_recorder import LiveAudioRecorder
except ImportError as e:
    print(f"Error importing custom modules: {e}")
    print("Make sure you're running from the backend directory and all files are present.")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Wildlife Audio Classification System", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model_loader = None
audio_classifier = None
audio_preprocessor = None
database = None
live_recorder = None
executor = ThreadPoolExecutor(max_workers=5)  # For handling 5 concurrent audio files

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.recording_status = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize models and database on startup"""
    global model_loader, audio_classifier, audio_preprocessor, database, live_recorder
    
    try:
        logger.info("Initializing system...")
        
        # Load ML models
        logger.info("Loading models...")
        model_loader = ModelLoader()
        audio_classifier = AudioClassifier(model_loader)
        audio_preprocessor = AudioPreprocessor(target_sr=22050, target_duration=30)
        
        # Initialize database
        logger.info("Initializing database...")
        database = AudioDetectionDB()
        
        # Initialize live recorder (but don't start recording yet)
        logger.info("Initializing live audio recorder...")
        live_recorder = LiveAudioRecorder(chunk_duration=30)
        live_recorder.set_chunk_processor(process_live_audio_chunk)
        
        logger.info("System initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise

def process_live_audio_chunk(filename: str, chunk_data: dict):
    """Process live audio chunks from the recorder"""
    try:
        logger.info(f"Processing live audio chunk: {filename}")
        
        # Extract features
        features = audio_preprocessor.extract_features_enhanced(filename)
        if not features:
            logger.error("Failed to extract features from live audio chunk")
            return
        
        # Get predictions
        gunshot_results = audio_classifier.predict_gunshot(features)
        wildlife_results = audio_classifier.predict_wildlife(features)
        
        # Process results and add to database
        all_results = []
        
        # Process gunshot results
        for model_name, result in gunshot_results.items():
            if result.get('prediction') != 'Error':
                detection_id = database.add_detection(
                    detection_type='gunshot',
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    model_name=model_name,
                    probabilities=result['probabilities'],
                    audio_filename=filename,
                    is_live=True
                )
                
                result['detection_id'] = detection_id
                result['timestamp'] = chunk_data['timestamp']
                all_results.append(result)
        
        # Process wildlife results
        for model_name, result in wildlife_results.items():
            if result.get('prediction') != 'Error':
                detection_id = database.add_detection(
                    detection_type='wildlife',
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    model_name=model_name,
                    probabilities=result['probabilities'],
                    audio_filename=filename,
                    is_live=True
                )
                
                result['detection_id'] = detection_id
                result['timestamp'] = chunk_data['timestamp']
                all_results.append(result)
        
        # Broadcast results to connected clients
        asyncio.create_task(manager.broadcast({
            'type': 'live_detection',
            'data': {
                'chunk_timestamp': chunk_data['timestamp'],
                'results': all_results,
                'audio_level': live_recorder.get_current_audio_level() if live_recorder else 0
            }
        }))
        
        # Clean up temporary file
        try:
            os.unlink(filename)
        except Exception as e:
            logger.warning(f"Failed to delete temp file {filename}: {e}")
            
    except Exception as e:
        logger.error(f"Error processing live audio chunk: {e}")

def process_single_audio(file_content: bytes, filename: str) -> Dict:
    """
    Process a single audio file and return predictions
    """
    try:
        start_time = time.time()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Extract features with better audio handling
        try:
            # Use AudioPreprocessor with intelligent duration handling
            processor = AudioPreprocessor(
                target_sr=22050, 
                target_duration=30,  # Use 30 seconds max, but better handling
                normalize_audio=True
            )
            
            # Extract features with preprocessing
            features = processor.extract_features_enhanced(temp_file_path)
            
            if features is None:
                return {
                    'filename': filename,
                    'success': False,
                    'error': 'Failed to extract features',
                    'processing_time': time.time() - start_time
                }
            
            # Ensure audio_classifier is initialized
            if audio_classifier is None:
                return {
                    'filename': filename,
                    'success': False,
                    'error': 'Audio classifier is not initialized',
                    'processing_time': time.time() - start_time
                }

            # Classify audio
            classification_result = audio_classifier.classify_audio(features)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            processing_time = time.time() - start_time
            
            return {
                'filename': filename,
                'success': True,
                'classification': classification_result,
                'processing_time': processing_time,
                'feature_count': len(features)
            }
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        return {
            'filename': filename,
            'success': False,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@app.post("/upload_audio")
async def upload_audio_files(files: List[UploadFile] = File(...)):
    """
    Upload and process up to 5 audio files simultaneously
    """
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file types
    allowed_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}
    for file in files:
        filename = file.filename if file.filename is not None else "uploaded_audio.wav"
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} has unsupported format. Allowed: {allowed_extensions}"
            )
    
    try:
        # Read all files
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((content, file.filename))
        
        # Process files concurrently
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor, 
                process_single_audio, 
                content, 
                filename
            ) 
            for content, filename in file_data
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Find best overall prediction
        best_overall = None
        best_confidence = 0.0
        
        for result in results:
            if result['success'] and result['classification']['success']:
                best_result = result['classification']['best_result']
                if best_result and best_result['best_confidence'] > best_confidence:
                    best_confidence = best_result['best_confidence']
                    best_overall = {
                        'filename': result['filename'],
                        'prediction': best_result['best_prediction'],
                        'confidence': best_result['best_confidence'],
                        'model': best_result['best_model']
                    }
        
        return {
            'success': True,
            'total_files': len(files),
            'results': results,
            'best_overall_prediction': best_overall,
            'processing_summary': {
                'total_processing_time': sum(r.get('processing_time', 0) for r in results),
                'successful_files': sum(1 for r in results if r['success']),
                'failed_files': sum(1 for r in results if not r['success'])
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing audio files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio processing
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'audio_chunk':
                # Handle audio chunk data
                # This would be used for streaming audio processing
                await manager.send_personal_message({
                    'type': 'status',
                    'message': 'Audio chunk received, processing...'
                }, websocket)
                
            elif message.get('type') == 'ping':
                # Handle ping
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': time.time()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'models_loaded': {
            'gunshot_models': len(model_loader.gunshot_models) if model_loader else 0,
            'wildlife_models': len(model_loader.wildlife_models) if model_loader else 0,
            'scalers': len(model_loader.scalers) if model_loader else 0
        },
        'timestamp': time.time()
    }

@app.get("/models/info")
async def get_models_info():
    """Get information about loaded models"""
    if not model_loader:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    return {
        'gunshot_models': list(model_loader.gunshot_models.keys()),
        'wildlife_models': list(model_loader.wildlife_models.keys()),
        'scalers': list(model_loader.scalers.keys()),
        'total_models': len(model_loader.gunshot_models) + len(model_loader.wildlife_models)
    }

@app.post("/classify_single")
async def classify_single_audio(file: UploadFile = File(...)):
    """
    Classify a single audio file
    """
    try:
        content = await file.read()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, 
            process_single_audio, 
            content, 
            file.filename if file.filename is not None else "uploaded_audio.wav"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing single audio file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API Endpoints

@app.post("/live-recording/start")
async def start_live_recording():
    """Start live audio recording"""
    global live_recorder
    
    if not live_recorder:
        raise HTTPException(status_code=500, detail="Live recorder not initialized")
    
    if live_recorder.is_recording:
        return {"status": "already_recording", "message": "Live recording already in progress"}
    
    try:
        live_recorder.start_recording()
        manager.recording_status = True
        
        # Broadcast status to connected clients
        await manager.broadcast({
            'type': 'recording_status',
            'status': 'started',
            'timestamp': time.time()
        })
        
        # Log to database
        if database:
            database.log_system_status('recording', 'started', 'Live recording session started')
        
        return {"status": "started", "message": "Live recording started successfully"}
        
    except Exception as e:
        logger.error(f"Failed to start live recording: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start recording: {str(e)}")

@app.post("/live-recording/stop")
async def stop_live_recording():
    """Stop live audio recording"""
    global live_recorder
    
    if not live_recorder:
        raise HTTPException(status_code=500, detail="Live recorder not initialized")
    
    if not live_recorder.is_recording:
        return {"status": "not_recording", "message": "No active recording to stop"}
    
    try:
        live_recorder.stop_recording()
        manager.recording_status = False
        
        # Broadcast status to connected clients
        await manager.broadcast({
            'type': 'recording_status',
            'status': 'stopped',
            'timestamp': time.time()
        })
        
        # Log to database
        if database:
            database.log_system_status('recording', 'stopped', 'Live recording session stopped')
        
        return {"status": "stopped", "message": "Live recording stopped successfully"}
        
    except Exception as e:
        logger.error(f"Failed to stop live recording: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop recording: {str(e)}")

@app.get("/live-recording/status")
async def get_recording_status():
    """Get current recording status"""
    if not live_recorder:
        return {"is_recording": False, "error": "Live recorder not initialized"}
    
    return {
        "is_recording": live_recorder.is_recording,
        "current_audio_level": live_recorder.get_current_audio_level() if live_recorder.is_recording else 0,
        "connected_clients": len(manager.active_connections)
    }

@app.get("/detections/recent")
async def get_recent_detections(limit: int = 10, detection_type: Optional[str] = None):
    """Get recent detections from database"""
    if not database:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        detections = database.get_recent_detections(limit=limit, detection_type=detection_type)
        return {"detections": detections}
    except Exception as e:
        logger.error(f"Failed to get recent detections: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/detections/stats")
async def get_detection_stats(hours: int = 24):
    """Get detection statistics"""
    if not database:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        stats = database.get_detection_stats(hours=hours)
        return {"stats": stats}
    except Exception as e:
        logger.error(f"Failed to get detection stats: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/wildlife/counts")
async def get_animal_counts():
    """Get animal count statistics"""
    if not database:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        counts = database.get_animal_counts()
        return {"animal_counts": counts}
    except Exception as e:
        logger.error(f"Failed to get animal counts: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/upload/single")
async def upload_single_file(file: UploadFile = File(...)):
    """Upload and analyze a single audio file with database storage"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    if not file.filename.lower().endswith(('.wav', '.mp3', '.flac', '.m4a', '.ogg')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process the audio file
        result = await asyncio.get_event_loop().run_in_executor(
            executor, process_single_audio, file_content, file.filename
        )
        
        # Store results in database if successful
        if result.get('success') and database:
            # Store gunshot results
            if 'gunshot_results' in result:
                for model_name, gunshot_result in result['gunshot_results'].items():
                    if gunshot_result.get('prediction') != 'Error':
                        database.add_detection(
                            detection_type='gunshot',
                            prediction=gunshot_result['prediction'],
                            confidence=gunshot_result['confidence'],
                            model_name=model_name,
                            probabilities=gunshot_result['probabilities'],
                            audio_filename=file.filename,
                            processing_time=result.get('processing_time'),
                            is_live=False
                        )
            
            # Store wildlife results
            if 'wildlife_results' in result:
                for model_name, wildlife_result in result['wildlife_results'].items():
                    if wildlife_result.get('prediction') != 'Error':
                        database.add_detection(
                            detection_type='wildlife',
                            prediction=wildlife_result['prediction'],
                            confidence=wildlife_result['confidence'],
                            model_name=model_name,
                            probabilities=wildlife_result['probabilities'],
                            audio_filename=file.filename,
                            processing_time=result.get('processing_time'),
                            is_live=False
                        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to process uploaded file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    print("Starting Audio Classification Middleware...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
