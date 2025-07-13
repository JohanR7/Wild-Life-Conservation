import torch
import torchaudio
import torchaudio.transforms as T
import pandas as pd
import numpy as np
import librosa
from concurrent.futures import ThreadPoolExecutor
import os
from sklearn.preprocessing import StandardScaler, RobustScaler
import warnings
warnings.filterwarnings('ignore')

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

class AudioPreprocessor:
    """
    Comprehensive audio preprocessing pipeline with enhanced feature extraction
    """
    def __init__(self, target_sr=22050, target_duration=30, normalize_audio=True):
        self.target_sr = target_sr
        self.target_duration = target_duration  # Can be None for variable length
        self.normalize_audio = normalize_audio
        self.feature_scaler = None
        
    def validate_audio(self, waveform, sr, file_path=None):
        """
        Validate audio file for common issues
        """
        # Check for empty audio
        if waveform.shape[-1] == 0:
            raise ValueError("Empty audio file")
            
        # Check for extremely short audio (< 0.1 seconds)
        if waveform.shape[-1] < sr * 0.1:
            raise ValueError("Audio too short (< 0.1 seconds)")
            
        # Check for NaN or infinite values
        if torch.isnan(waveform).any() or torch.isinf(waveform).any():
            raise ValueError("Audio contains NaN or infinite values")
            
        # Check for silent audio (very low energy)
        energy = torch.mean(torch.abs(waveform))
        if energy < 1e-6:
            raise ValueError("Audio appears to be silent")
            
        return True
    
    def resample_audio(self, waveform, original_sr):
        """
        Resample audio to target sample rate
        """
        if original_sr != self.target_sr:
            resampler = T.Resample(original_sr, self.target_sr).to(device)
            waveform = resampler(waveform)
        return waveform, self.target_sr
    
    def normalize_audio_amplitude(self, waveform, method='peak'):
        """
        Normalize audio amplitude
        """
        if not self.normalize_audio:
            return waveform
            
        if method == 'peak':
            # Peak normalization
            max_val = torch.max(torch.abs(waveform))
            if max_val > 0:
                waveform = waveform / max_val
        elif method == 'rms':
            # RMS normalization
            rms = torch.sqrt(torch.mean(waveform ** 2))
            if rms > 0:
                waveform = waveform / rms * 0.1  # Scale to reasonable level
        elif method == 'zscore':
            # Z-score normalization
            mean = torch.mean(waveform)
            std = torch.std(waveform)
            if std > 0:
                waveform = (waveform - mean) / std
                
        return waveform
    
    def handle_duration(self, waveform, sr, method='crop_pad'):
        """
        Handle variable duration audio
        """
        # If target_duration is None, use the full audio
        if self.target_duration is None:
            return waveform
            
        target_length = int(sr * self.target_duration)
        current_length = waveform.shape[-1]
        
        if method == 'crop_pad':
            if current_length > target_length:
                # Crop from center
                start = (current_length - target_length) // 2
                waveform = waveform[..., start:start + target_length]
            elif current_length < target_length:
                # Pad with zeros
                pad_length = target_length - current_length
                waveform = torch.nn.functional.pad(waveform, (0, pad_length))
                
        elif method == 'segment':
            # Split long audio into segments
            if current_length > target_length:
                segments = []
                for i in range(0, current_length, target_length):
                    segment = waveform[..., i:i + target_length]
                    if segment.shape[-1] == target_length:
                        segments.append(segment)
                return segments  # Return list of segments
            else:
                # Pad short audio
                pad_length = target_length - current_length
                waveform = torch.nn.functional.pad(waveform, (0, pad_length))
                
        return waveform
    
    def remove_silence(self, waveform, sr, threshold_db=-40):
        """
        Remove silence from beginning and end of audio
        """
        # Convert to numpy for librosa
        audio_np = waveform.cpu().numpy().flatten()
        
        # Trim silence
        trimmed, _ = librosa.effects.trim(audio_np, top_db=-threshold_db)
        
        # Convert back to tensor
        return torch.tensor(trimmed).unsqueeze(0).to(device)
    
    def apply_audio_filters(self, waveform, sr):
        """
        Apply basic audio filters
        """
        audio_np = waveform.cpu().numpy().flatten()
        
        # High-pass filter to remove DC offset and low-frequency noise
        audio_filtered = librosa.effects.preemphasis(audio_np, coef=0.97)
        
        return torch.tensor(audio_filtered).unsqueeze(0).to(device)

    def extract_features_enhanced(self, file_path_or_waveform, sr=None):
        """
        Enhanced feature extraction that can work with file paths or waveform data
        Extracts the same features as the enhanced version from your second code
        """
        try:
            # Handle both file paths and direct waveform input
            if isinstance(file_path_or_waveform, str):
                # Load from file path
                waveform, sr = torchaudio.load(file_path_or_waveform)
            else:
                # Use provided waveform and sample rate
                waveform = file_path_or_waveform
                if sr is None:
                    raise ValueError("Sample rate must be provided when using waveform input")
            
            # Move to device for torchaudio transforms
            waveform_torch = waveform.to(device)

            # Convert to mono
            if waveform_torch.shape[0] > 1:
                waveform_torch = torch.mean(waveform_torch, dim=0, keepdim=True)
                
            # For librosa, we need a NumPy array on the CPU
            waveform_np = waveform.numpy().flatten()

            # --- Feature Extraction ---
            features = {}

            # 1. MFCCs (using torchaudio) - Keep only first 13 coefficients
            mfcc_transform = T.MFCC(
                sample_rate=sr, 
                n_mfcc=13  # Reduced from 20, dropping highly correlated higher-order coefficients
            ).to(device)
            mfccs = mfcc_transform(waveform_torch).squeeze(0).cpu().numpy()
            
            # 2. Delta MFCCs (first-order derivatives)
            delta_mfccs = librosa.feature.delta(mfccs, order=1)
            
            # 3. Delta-Delta MFCCs (second-order derivatives)
            delta2_mfccs = librosa.feature.delta(mfccs, order=2)
            
            # 4. Chroma Features (mean only, dropping std)
            chroma = librosa.feature.chroma_stft(y=waveform_np, sr=sr)
            
            # 5. Spectral Contrast (mean only, dropping std)
            mel_spec = librosa.feature.melspectrogram(y=waveform_np, sr=sr, n_mels=128)
            contrast = librosa.feature.spectral_contrast(S=librosa.power_to_db(mel_spec), sr=sr)
            
            # 6. Zero Crossing Rate (mean only, dropping std)
            zcr = librosa.feature.zero_crossing_rate(y=waveform_np)
            
            # 7. RMS Energy (for quantiles, dropping std)
            rms = librosa.feature.rms(y=waveform_np)
            
            # 8. Spectral Centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=waveform_np, sr=sr)
            
            # 9. Spectral Bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=waveform_np, sr=sr)
            
            # REMOVED: Spectral Roll-off computation (not needed for 60-feature match)
            # spectral_rolloff_85 = librosa.feature.spectral_rolloff(y=waveform_np, sr=sr, roll_percent=0.85)
            
            # 11. Spectral Flatness
            spectral_flatness = librosa.feature.spectral_flatness(y=waveform_np)
            
            # 12. Onset Strength Envelope
            onset_strength = librosa.onset.onset_strength(y=waveform_np, sr=sr)
            
            # --- Summarize features over time ---
            final_features = {}
            
            # MFCC features (mean and std for first 13 coefficients)
            final_features.update({
                f'mfcc_{i}_mean': np.mean(mfccs[i]) for i in range(13)
            })
            final_features.update({
                f'mfcc_{i}_std': np.std(mfccs[i]) for i in range(13)
            })
            
            # Delta MFCC features (mean only, REDUCED to 8 to match 60-feature training)
            final_features.update({
                f'delta_mfcc_{i}_mean': np.mean(delta_mfccs[i]) for i in range(8)  # Reduced from 13 to 8
            })
            
            # Delta-Delta MFCC features (mean only, first 7 coefficients only)
            final_features.update({
                f'delta2_mfcc_{i}_mean': np.mean(delta2_mfccs[i]) for i in range(7)
            })
            
            # Chroma features (mean only, key bins: 0, 3, 6 for tonal coverage without redundancy)
            key_chroma_bins = [0, 3, 6]
            final_features.update({
                f'chroma_{i}_mean': np.mean(chroma[i]) for i in key_chroma_bins
            })
            
            # Spectral Contrast features (mean only, all 6 bins except highly correlated ones)
            contrast_bins = list(range(6))  # Use all 6 bins as in the second code
            final_features.update({
                f'contrast_{i}_mean': np.mean(contrast[i]) for i in contrast_bins
            })
            
            # Zero Crossing Rate (mean only, dropping std)
            final_features['zcr_mean'] = np.mean(zcr)
            
            # RMS Energy (mean only, dropping std)
            final_features['rms_mean'] = np.mean(rms)
            
            # RMS Energy Quantiles (75% for robust loudness detection)
            final_features['rms_q75'] = np.percentile(rms, 75)
            
            # Spectral Centroid (mean and std)
            final_features['spectral_centroid_mean'] = np.mean(spectral_centroid)
            final_features['spectral_centroid_std'] = np.std(spectral_centroid)
            
            # Spectral Bandwidth (mean and std)
            final_features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
            final_features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
            
            # REMOVED: Spectral Roll-off to match original 60-feature training
            # final_features['spectral_rolloff_mean'] = np.mean(spectral_rolloff_85)
            
            # Spectral Flatness (mean only, dropping std as it's often noise)
            final_features['spectral_flatness_mean'] = np.mean(spectral_flatness)
            
            # Onset Strength (mean and max)
            final_features['onset_strength_mean'] = np.mean(onset_strength)
            final_features['onset_strength_max'] = np.max(onset_strength)
            
            return final_features

        except Exception as e:
            print(f"Error processing audio: {e}")
            return None

    def preprocess_audio(self, file_path_or_waveform, sr=None, apply_filters=True, 
                        remove_silence_flag=True, duration_method='crop_pad'):
        """
        Complete preprocessing pipeline
        """
        try:
            # Handle both file paths and direct waveform input
            if isinstance(file_path_or_waveform, str):
                waveform, original_sr = torchaudio.load(file_path_or_waveform)
            else:
                waveform = file_path_or_waveform
                original_sr = sr
                if sr is None:
                    raise ValueError("Sample rate must be provided when using waveform input")
            
            # Move to device
            waveform = waveform.to(device)
            
            # Validate audio
            self.validate_audio(waveform, original_sr)
            
            # Convert to mono if needed
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample if needed
            waveform, sr = self.resample_audio(waveform, original_sr)
            
            # Remove silence
            if remove_silence_flag:
                waveform = self.remove_silence(waveform, sr)
            
            # Apply filters
            if apply_filters:
                waveform = self.apply_audio_filters(waveform, sr)
            
            # Normalize amplitude
            waveform = self.normalize_audio_amplitude(waveform)
            
            # Handle duration
            waveform = self.handle_duration(waveform, sr, method=duration_method)
            
            return waveform, sr
            
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return None, None

    def process_and_extract_features(self, file_path_or_waveform, sr=None, 
                                   apply_preprocessing=True, **preprocessing_kwargs):
        """
        Complete pipeline: preprocessing + feature extraction
        """
        if apply_preprocessing:
            # Apply preprocessing first
            processed_waveform, processed_sr = self.preprocess_audio(
                file_path_or_waveform, sr, **preprocessing_kwargs
            )
            if processed_waveform is None:
                return None
            
            # Extract features from processed audio
            return self.extract_features_enhanced(processed_waveform, processed_sr)
        else:
            # Extract features directly without preprocessing
            return self.extract_features_enhanced(file_path_or_waveform, sr)

    def get_feature_names(self):
        """
        Get the names of all features that will be extracted
        """
        feature_names = []
        
        # MFCC features (mean and std for first 13 coefficients)
        for i in range(13):
            feature_names.append(f'mfcc_{i}_mean')
            feature_names.append(f'mfcc_{i}_std')
        
        # Delta MFCC features (mean only, REDUCED from 13 to 8 to match training)
        for i in range(8):  # Reduced from 13 to 8
            feature_names.append(f'delta_mfcc_{i}_mean')
        
        # Delta-Delta MFCC features (mean only, first 7 coefficients only)
        for i in range(7):
            feature_names.append(f'delta2_mfcc_{i}_mean')
        
        # Chroma features (key bins: 0, 3, 6)
        for i in [0, 3, 6]:
            feature_names.append(f'chroma_{i}_mean')
        
        # Spectral Contrast features (all 6 bins)
        for i in range(6):
            feature_names.append(f'contrast_{i}_mean')
        
        # Other features (REDUCED to match 60-feature training)
        feature_names.extend([
            'zcr_mean',
            'rms_mean',
            'rms_q75',
            'spectral_centroid_mean',
            'spectral_centroid_std',
            'spectral_bandwidth_mean',
            'spectral_bandwidth_std',
            # REMOVED: 'spectral_rolloff_mean' - not in actual extraction
            'spectral_flatness_mean',
            'onset_strength_mean',
            'onset_strength_max'
        ])
        
        return feature_names

    def get_feature_count(self):
        """
        Get the total number of features that will be extracted
        """
        return len(self.get_feature_names())

# Standalone function for compatibility with main.py imports
def extract_features_enhanced(file_path):
    """
    Standalone version of feature extraction for backward compatibility
    """
    processor = AudioPreprocessor(target_sr=22050, target_duration=30)
    return processor.extract_features_enhanced(file_path)

# Example usage
if __name__ == "__main__":
    # Initialize the processor
    processor = AudioPreprocessor(target_sr=22050, target_duration=30)
    
    # Example 1: Extract features from a file path
    # features = processor.extract_features_enhanced("path/to/audio.wav")
    
    # Example 2: Preprocess and then extract features
    # features = processor.process_and_extract_features("path/to/audio.wav")
    
    # Example 3: Extract features from waveform data
    # waveform, sr = torchaudio.load("path/to/audio.wav")
    # features = processor.extract_features_enhanced(waveform, sr)
    
    # Get feature information
    print(f"Total features: {processor.get_feature_count()}")
    print(f"Feature names: {processor.get_feature_names()}")
    
    # Feature breakdown
    print("\n📋 Feature Summary:")
    print(f"  • MFCC (0-12): mean + std = 26 features")
    print(f"  • Delta MFCC (0-12): mean only = 13 features") 
    print(f"  • Delta² MFCC (0-6): mean only = 7 features")
    print(f"  • Chroma (key bins 0,3,6): mean only = 3 features")
    print(f"  • Spectral Contrast (all 6 bins): mean only = 6 features")
    print(f"  • ZCR: mean only = 1 feature")
    print(f"  • RMS: mean + quantiles = 2 features")
    print(f"  • Spectral Centroid: mean + std = 2 features")
    print(f"  • Spectral Bandwidth: mean + std = 2 features")
    print(f"  • Spectral Roll-off (85%): mean only = 1 feature")
    print(f"  • Spectral Flatness: mean only = 1 feature")
    print(f"  • Onset Strength: mean + max = 2 features")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Total: {processor.get_feature_count()} features (optimized for gunshot/human/wildlife)")