# Audio Classification Middleware Configuration

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
MAX_WORKERS = 5
MAX_FILES_PER_REQUEST = 5

# Audio Processing Configuration
TARGET_SAMPLE_RATE = 22050
TARGET_DURATION = 30  # seconds
NORMALIZE_AUDIO = True

# Model Configuration
MODEL_BASE_PATH = "../ml_models"

# File Upload Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# CORS Configuration
CORS_ORIGINS = ["*"]  # In production, specify your frontend URLs

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL = 30  # seconds
