#!/usr/bin/env python3
"""
Database manager for audio detection storage
"""

import sqlite3
import json
from typing import Dict, List, Optional

class AudioDetectionDB:
    def __init__(self, db_path: str = "audio_detections.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                detection_type TEXT NOT NULL,  -- 'gunshot' or 'wildlife'
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                model_name TEXT NOT NULL,
                probabilities TEXT,  -- JSON string
                audio_filename TEXT,
                processing_time REAL,
                is_live_recording BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create animal_counts table for wildlife statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS animal_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_name TEXT UNIQUE NOT NULL,
                count INTEGER DEFAULT 0,
                last_detected DATETIME
            )
        ''')
        
        # Create system_status table for monitoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status_type TEXT NOT NULL,  -- 'connection', 'recording', 'processing'
                status_value TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_detection(self, detection_type: str, prediction: str, confidence: float, 
                     model_name: str, probabilities: Dict, audio_filename: Optional[str] = None,
                     processing_time: Optional[float] = None, is_live: bool = False) -> int:
        """Add a new detection to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detections 
            (detection_type, prediction, confidence, model_name, probabilities, 
             audio_filename, processing_time, is_live_recording)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (detection_type, prediction, confidence, model_name, 
              json.dumps(probabilities), audio_filename, processing_time, is_live))
        
        detection_id = cursor.lastrowid or 0
        
        # Update animal count if it's a wildlife detection and is a countable animal
        if detection_type == 'wildlife' and self.is_countable_animal(prediction):
            self.update_animal_count(prediction)
        
        conn.commit()
        conn.close()
        
        return detection_id
    
    def is_countable_animal(self, prediction: str) -> bool:
        """Check if the prediction is a countable animal (exclude vacuum, machinery, etc.)"""
        # ESC-50 non-animal classes to exclude
        non_animal_classes = {
            'Vacuum_cleaner', 'Engine', 'Chainsaw', 'Siren', 'Car_horn', 
            'Train', 'Clock_alarm', 'Clock_tick', 'Glass_breaking', 'Helicopter',
            'Airplane', 'Fireworks', 'Hand_saw', 'Can_opening', 'Washing_machine',
            'Water_drops', 'Toilet_flush', 'Thunderstorm', 'Rain', 'Sea_waves',
            'Crackling_fire', 'Wind', 'Footsteps', 'Door_wood_knock', 'Mouse_click',
            'Keyboard_typing', 'Door_wood_creaks', 'Breathing', 'Snoring', 'Coughing',
            'Sneezing', 'Crying_baby', 'Laughing', 'Clapping'
        }
        
        return prediction not in non_animal_classes
    
    def update_animal_count(self, animal_name: str):
        """Update count for a specific animal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if animal exists
        cursor.execute('SELECT count FROM animal_counts WHERE animal_name = ?', (animal_name,))
        result = cursor.fetchone()
        
        if result:
            # Update existing count
            cursor.execute('''
                UPDATE animal_counts 
                SET count = count + 1, last_detected = CURRENT_TIMESTAMP 
                WHERE animal_name = ?
            ''', (animal_name,))
        else:
            # Insert new animal
            cursor.execute('''
                INSERT INTO animal_counts (animal_name, count, last_detected)
                VALUES (?, 1, CURRENT_TIMESTAMP)
            ''', (animal_name,))
        
        conn.commit()
        conn.close()
    
    def get_recent_detections(self, limit: int = 10, detection_type: Optional[str] = None) -> List[Dict]:
        """Get recent detections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if detection_type:
            cursor.execute('''
                SELECT * FROM detections 
                WHERE detection_type = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (detection_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM detections 
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            detection = dict(zip(columns, row))
            if detection['probabilities']:
                detection['probabilities'] = json.loads(detection['probabilities'])
            results.append(detection)
        
        conn.close()
        return results
    
    def get_animal_counts(self) -> List[Dict]:
        """Get animal count statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT animal_name, count, last_detected 
            FROM animal_counts 
            ORDER BY count DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_detection_stats(self, hours: int = 24) -> Dict:
        """Get detection statistics for the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total detections
        cursor.execute('''
            SELECT COUNT(*) FROM detections 
            WHERE timestamp >= datetime('now', '-{} hours')
        '''.format(hours))
        total_detections = cursor.fetchone()[0]
        
        # Gunshot alerts
        cursor.execute('''
            SELECT COUNT(*) FROM detections 
            WHERE detection_type = 'gunshot' 
            AND timestamp >= datetime('now', '-{} hours')
        '''.format(hours))
        gunshot_alerts = cursor.fetchone()[0]
        
        # Wildlife sounds
        cursor.execute('''
            SELECT COUNT(*) FROM detections 
            WHERE detection_type = 'wildlife' 
            AND timestamp >= datetime('now', '-{} hours')
        '''.format(hours))
        wildlife_sounds = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute('''
            SELECT AVG(confidence) FROM detections 
            WHERE timestamp >= datetime('now', '-{} hours')
        '''.format(hours))
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_detections': total_detections,
            'gunshot_alerts': gunshot_alerts,
            'wildlife_sounds': wildlife_sounds,
            'avg_confidence': round(avg_confidence, 3)
        }
    
    def log_system_status(self, status_type: str, status_value: str, details: Optional[str] = None):
        """Log system status for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_status (status_type, status_value, details)
            VALUES (?, ?, ?)
        ''', (status_type, status_value, details))
        
        conn.commit()
        conn.close()

# Example usage and test
if __name__ == "__main__":
    db = AudioDetectionDB()
    
    # Test adding a detection
    detection_id = db.add_detection(
        detection_type='wildlife',
        prediction='Dog',
        confidence=0.85,
        model_name='xgboost_esc50',
        probabilities={'Dog': 0.85, 'Cat': 0.10, 'Sheep': 0.05},
        audio_filename='test_audio.wav',
        processing_time=1.2,
        is_live=True
    )
    
    print(f"Added detection with ID: {detection_id}")
    
    # Test getting recent detections
    recent = db.get_recent_detections(5)
    print(f"Recent detections: {len(recent)}")
    
    # Test getting stats
    stats = db.get_detection_stats()
    print(f"Detection stats: {stats}")
    
    # Test animal counts
    animals = db.get_animal_counts()
    print(f"Animal counts: {animals}")
