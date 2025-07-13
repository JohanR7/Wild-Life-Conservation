#!/usr/bin/env python3
"""
Live audio recording system with 30-second chunk processing
"""

import wave
import pyaudio
import threading
import queue
import time
import numpy as np
from typing import Callable, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LiveAudioRecorder:
    def __init__(self, 
                 chunk_duration: int = 30,  # 30 seconds per chunk
                 sample_rate: int = 44100,
                 channels: int = 1,
                 chunk_size: int = 1024,
                 audio_format=pyaudio.paInt16):
        
        self.chunk_duration = chunk_duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        
        # Audio processing
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        
        # Recording state
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.processing_queue = queue.Queue(maxsize=5)  # Max 5 chunks in queue
        self.processing_thread: Optional[threading.Thread] = None
        
        # Callback for processed audio
        self.on_chunk_processed: Optional[Callable] = None
        
        # Audio data storage
        self.current_chunk = []
        self.chunk_start_time = None
        
    def set_chunk_processor(self, callback: Callable):
        """Set callback function for processing audio chunks"""
        self.on_chunk_processed = callback
    
    def start_recording(self):
        """Start live audio recording"""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
        
        try:
            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.chunk_start_time = time.time()
            self.current_chunk = []
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_chunks)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.stream.start_stream()
            logger.info(f"Started live recording with {self.chunk_duration}s chunks")
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.stop_recording()
    
    def stop_recording(self):
        """Stop live audio recording"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Process any remaining audio in current chunk
        if self.current_chunk:
            self._queue_chunk_for_processing()
        
        # Signal processing thread to stop
        self.processing_queue.put(None)
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        logger.info("Stopped live recording")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream data"""
        if not self.is_recording:
            return (None, pyaudio.paComplete)
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.current_chunk.extend(audio_data)
        
        # Check if chunk duration is reached
        current_time = time.time()
        if self.chunk_start_time and current_time - self.chunk_start_time >= self.chunk_duration:
            self._queue_chunk_for_processing()
            self._start_new_chunk()
        
        return (None, pyaudio.paContinue)
    
    def _queue_chunk_for_processing(self):
        """Queue current chunk for processing"""
        if not self.current_chunk:
            return
        
        chunk_data = {
            'audio_data': np.array(self.current_chunk, dtype=np.int16),
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'timestamp': time.time(),
            'duration': self.chunk_duration
        }
        
        try:
            # Add to processing queue (non-blocking)
            self.processing_queue.put(chunk_data, block=False)
            logger.info(f"Queued {self.chunk_duration}s audio chunk for processing")
        except queue.Full:
            logger.warning("Processing queue full, dropping audio chunk")
    
    def _start_new_chunk(self):
        """Start recording a new chunk"""
        self.current_chunk = []
        self.chunk_start_time = time.time()
    
    def _process_chunks(self):
        """Process audio chunks from queue"""
        logger.info("Started audio chunk processing thread")
        
        while self.is_recording or not self.processing_queue.empty():
            try:
                # Get chunk from queue (with timeout)
                chunk_data = self.processing_queue.get(timeout=1)
                
                if chunk_data is None:  # Stop signal
                    break
                
                # Save chunk to temporary file
                temp_filename = self._save_chunk_to_file(chunk_data)
                
                # Process chunk if callback is set
                if self.on_chunk_processed:
                    try:
                        self.on_chunk_processed(temp_filename, chunk_data)
                    except Exception as e:
                        logger.error(f"Error in chunk processor: {e}")
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
        
        logger.info("Audio chunk processing thread stopped")
    
    def _save_chunk_to_file(self, chunk_data: dict) -> str:
        """Save audio chunk to temporary WAV file"""
        timestamp = int(chunk_data['timestamp'])
        filename = f"live_chunk_{timestamp}.wav"
        filepath = Path("temp_audio") / filename
        
        # Create directory if it doesn't exist
        filepath.parent.mkdir(exist_ok=True)
        
        # Save as WAV file
        with wave.open(str(filepath), 'wb') as wav_file:
            wav_file.setnchannels(chunk_data['channels'])
            wav_file.setsampwidth(self.pyaudio_instance.get_sample_size(self.audio_format))
            wav_file.setframerate(chunk_data['sample_rate'])
            wav_file.writeframes(chunk_data['audio_data'].tobytes())
        
        return str(filepath)
    
    def get_current_audio_level(self) -> float:
        """Get current audio level for visualization"""
        if not self.current_chunk:
            return 0.0
        
        # Calculate RMS of recent audio data
        recent_data = self.current_chunk[-1024:] if len(self.current_chunk) > 1024 else self.current_chunk
        if not recent_data:
            return 0.0
        
        rms = np.sqrt(np.mean(np.array(recent_data, dtype=np.float32) ** 2))
        # Normalize to 0-100 range
        return min(100.0, (rms / 32768.0) * 100.0)
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_recording()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def process_audio_chunk(filename: str, chunk_data: dict):
        print(f"Processing chunk: {filename}")
        print(f"Duration: {chunk_data['duration']}s")
        print(f"Sample rate: {chunk_data['sample_rate']}")
        print(f"Data shape: {chunk_data['audio_data'].shape}")
        # Here you would call your audio classification
    
    recorder = LiveAudioRecorder(chunk_duration=5)  # 5 seconds for testing
    recorder.set_chunk_processor(process_audio_chunk)
    
    try:
        recorder.start_recording()
        print("Recording... Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            level = recorder.get_current_audio_level()
            print(f"Audio level: {level:.1f}%")
            
    except KeyboardInterrupt:
        print("\nStopping recording...")
        recorder.cleanup()
