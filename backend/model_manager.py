import os
import joblib
import pandas as pd
from typing import Dict
import logging
import warnings
from pathlib import Path

# Suppress sklearn version warnings for model loading
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Loads and manages all ML models for gunshot and wildlife classification
    """
    def __init__(self, model_base_path: str = "../ml_models"):
        self.model_base_path = Path(model_base_path)
        self.gunshot_models = {}
        self.wildlife_models = {}
        self.scalers = {}
        self.load_all_models()
    
    def load_all_models(self):
        """Load all available models"""
        try:
            # Load gunshot models
            gunshot_path = self.model_base_path / "gun_shots"
            if gunshot_path.exists():
                self._load_gunshot_models(gunshot_path)
            
            # Load wildlife models
            wildlife_path = self.model_base_path / "wildlife"
            if wildlife_path.exists():
                self._load_wildlife_models(wildlife_path)
                
            logger.info(f"Loaded {len(self.gunshot_models)} gunshot models and {len(self.wildlife_models)} wildlife models")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def _load_gunshot_models(self, path: Path):
        """Load gunshot classification models"""
        # Removed SVM due to unrealistic confidence values
        model_files = {
            'xgboost': 'xgboost_model.pkl'
        }
        
        scaler_file = 'scaler.pkl'
        
        # Load scaler with warning suppression
        scaler_path = path / scaler_file
        if scaler_path.exists():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.scalers['gunshot'] = joblib.load(scaler_path)
                logger.info(f"Loaded gunshot scaler from {scaler_path}")
            except Exception as e:
                logger.error(f"Failed to load scaler: {e}")
        
        # Load models with warning suppression
        for model_name, filename in model_files.items():
            model_path = path / filename
            if model_path.exists():
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        model = joblib.load(model_path)
                    self.gunshot_models[model_name] = model
                    logger.info(f"Loaded gunshot model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load gunshot model {model_name}: {e}")
    
    def _load_wildlife_models(self, path: Path):
        """Load wildlife classification models"""
        model_files = {
            'lightgbm_inat': 'lightgbm_inat_overfitting.pkl',
            'rf_esc50': 'rf_model_esc50.pkl',
            'xgboost_inat': 'xgboost_inat_overfitting.pkl',
            'xgboost_esc50': 'xgboost_model_esc50.pkl'
        }
        
        # Load models with warning suppression and better error handling
        for model_name, filename in model_files.items():
            model_path = path / filename
            if model_path.exists():
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        model = joblib.load(model_path)
                    
                    # Test if the model can make a simple prediction
                    if hasattr(model, 'predict'):
                        # Create a dummy feature array to test compatibility
                        import numpy as np
                        dummy_features = np.zeros((1, 60))  # Assuming 60 features
                        try:
                            model.predict(dummy_features)  # Test prediction
                            self.wildlife_models[model_name] = model
                            logger.info(f"Loaded wildlife model: {model_name}")
                        except Exception as test_e:
                            logger.warning(f"Model {model_name} loaded but failed prediction test: {test_e}")
                            logger.warning(f"Skipping {model_name} due to compatibility issues")
                    else:
                        logger.error(f"Model {model_name} doesn't have predict method")
                        
                except Exception as e:
                    logger.error(f"Failed to load wildlife model {model_name}: {e}")
                    # Continue loading other models even if one fails

class AudioClassifier:
    """
    Main classifier that uses all loaded models to make predictions
    """
    def __init__(self, model_loader: ModelLoader):
        self.model_loader = model_loader
        
        # Define class mappings based on actual model training
        # Gunshot models appear to have 4 classes (0,1,2,3)
        self.gunshot_classes = {
            0: "Quiet/Silent",
            1: "Gunshot", 
            2: "Other_Sound",
            3: "Noise/Disturbance"
        }
        
        # ESC-50 environmental sound classes (50 categories)
        self.esc50_classes = {
            0: "Dog", 1: "Rooster", 2: "Pig", 3: "Cow", 4: "Frog",
            5: "Cat", 6: "Hen", 7: "Insects", 8: "Sheep", 9: "Crow",
            10: "Rain", 11: "Sea_waves", 12: "Crackling_fire", 13: "Crickets", 14: "Chirping_birds",
            15: "Water_drops", 16: "Wind", 17: "Pouring_water", 18: "Toilet_flush", 19: "Thunderstorm",
            20: "Crying_baby", 21: "Sneezing", 22: "Clapping", 23: "Breathing", 24: "Coughing",
            25: "Footsteps", 26: "Laughing", 27: "Brushing_teeth", 28: "Snoring", 29: "Drinking_sipping",
            30: "Door_wood_knock", 31: "Mouse_click", 32: "Keyboard_typing", 33: "Door_wood_creaks", 34: "Can_opening",
            35: "Washing_machine", 36: "Vacuum_cleaner", 37: "Clock_alarm", 38: "Clock_tick", 39: "Glass_breaking",
            40: "Helicopter", 41: "Chainsaw", 42: "Siren", 43: "Car_horn", 44: "Engine",
            45: "Train", 46: "Church_bells", 47: "Airplane", 48: "Fireworks", 49: "Hand_saw"
        }
        
        # iNaturalist models have too many classes (~292) to hardcode here
        # We'll use generic naming for these and let users map them as needed
        self.inat_classes = {i: f"Species_{i}" for i in range(300)}  # Covering up to 300 classes
    
    def predict_gunshot(self, features: Dict) -> Dict:
        """
        Predict if audio contains gunshot using all gunshot models
        """
        results = {}
        
        # Convert features to DataFrame for consistency
        feature_df = pd.DataFrame([features])
        
        # Scale features if scaler is available
        if 'gunshot' in self.model_loader.scalers:
            try:
                scaled_features = self.model_loader.scalers['gunshot'].transform(feature_df)
                feature_array = scaled_features
            except Exception as e:
                logger.warning(f"Error scaling features for gunshot prediction: {e}")
                feature_array = feature_df.values
        else:
            feature_array = feature_df.values
        
        # Get predictions from all gunshot models
        for model_name, model in self.model_loader.gunshot_models.items():
            try:
                # Get prediction and probability
                prediction = model.predict(feature_array)[0]
                
                # Get probability if available (XGBoost has predict_proba)
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(feature_array)[0]
                    confidence = max(probabilities)
                    prob_dict = {self.gunshot_classes[i]: prob for i, prob in enumerate(probabilities)}
                else:
                    confidence = 0.5  # Default confidence
                    prob_dict = {class_name: 0.5 for class_name in self.gunshot_classes.values()}
                
                results[model_name] = {
                    'prediction': self.gunshot_classes.get(prediction, f"Class_{prediction}"),
                    'confidence': float(confidence),
                    'probabilities': {k: float(v) for k, v in prob_dict.items()},  # Convert numpy types
                    'model_type': 'gunshot'
                }
                
            except Exception as e:
                logger.error(f"Error with gunshot model {model_name}: {e}")
                results[model_name] = {
                    'prediction': 'Error',
                    'confidence': 0.0,
                    'probabilities': {},
                    'model_type': 'gunshot',
                    'error': str(e)
                }
        
        return results
    
    def predict_wildlife(self, features: Dict) -> Dict:
        """
        Predict wildlife/environmental sounds using all wildlife models
        """
        results = {}
        
        # Convert features to DataFrame for consistency
        feature_df = pd.DataFrame([features])
        feature_array = feature_df.values
        
        # Get predictions from all wildlife models
        for model_name, model in self.model_loader.wildlife_models.items():
            try:
                # Get prediction
                prediction = model.predict(feature_array)[0]
                
                # Choose the appropriate class mapping based on model type
                if "esc50" in model_name:
                    class_mapping = self.esc50_classes
                    model_type = "ESC-50"
                elif "inat" in model_name:
                    class_mapping = self.inat_classes
                    model_type = "iNaturalist"
                else:
                    # Fallback for unknown models
                    class_mapping = {i: f"Class_{i}" for i in range(500)}
                    model_type = "Unknown"
                
                # Get probability if available
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(feature_array)[0]
                    confidence = max(probabilities)
                    # Create probability dictionary using appropriate class mappings
                    prob_dict = {class_mapping.get(i, f"Class_{i}"): prob for i, prob in enumerate(probabilities)}
                else:
                    confidence = 0.5  # Default confidence
                    prob_dict = {class_mapping.get(prediction, f"Class_{prediction}"): 1.0}
                
                results[model_name] = {
                    'prediction': class_mapping.get(prediction, f"Class_{prediction}"),
                    'confidence': float(confidence),
                    'probabilities': {k: float(v) for k, v in prob_dict.items()},  # Convert numpy types
                    'model_type': f'wildlife_{model_type}'
                }
                
            except Exception as e:
                logger.error(f"Error with wildlife model {model_name}: {e}")
                results[model_name] = {
                    'prediction': 'Error',
                    'confidence': 0.0,
                    'probabilities': {},
                    'model_type': 'wildlife',
                    'error': str(e)
                }
        
        return results
    
    def get_best_prediction(self, all_results: Dict) -> Dict:
        """
        Get the best prediction across all models based on confidence score
        """
        best_prediction = None
        best_confidence = 0.0
        best_model = None
        
        for model_name, result in all_results.items():
            if 'error' not in result and result['confidence'] > best_confidence:
                best_confidence = result['confidence']
                best_prediction = result['prediction']
                best_model = model_name
        
        return {
            'best_prediction': best_prediction,
            'best_confidence': float(best_confidence) if best_confidence is not None else 0.0,
            'best_model': best_model,
            'all_predictions': all_results
        }
    
    def classify_audio(self, features: Dict) -> Dict:
        """
        Main classification method that runs all models and returns the best prediction
        """
        try:
            # Get gunshot predictions
            gunshot_results = self.predict_gunshot(features)
            
            # Get wildlife predictions
            wildlife_results = self.predict_wildlife(features)
            
            # Combine all results
            all_results = {**gunshot_results, **wildlife_results}
            
            # Get best prediction
            best_result = self.get_best_prediction(all_results)
            
            return {
                'success': True,
                'gunshot_predictions': gunshot_results,
                'wildlife_predictions': wildlife_results,
                'best_result': best_result,
                'total_models': len(all_results)
            }
            
        except Exception as e:
            logger.error(f"Error in classification: {e}")
            return {
                'success': False,
                'error': str(e),
                'gunshot_predictions': {},
                'wildlife_predictions': {},
                'best_result': None,
                'total_models': 0
            }
