import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import pickle
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Network traffic anomaly detection using multiple algorithms"""
    
    def __init__(self, model_type: str = "isolation_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'packet_size', 'duration', 'src_bytes', 'dst_bytes',
            'src_pkts', 'dst_pkts', 'src_port', 'dst_port'
        ]
        self.threshold = 0.5
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for anomaly detection"""
        # Select and create features
        features = []
        
        for col in self.feature_columns:
            if col in data.columns:
                features.append(data[col].fillna(0).values)
            else:
                features.append(np.zeros(len(data)))
        
        X = np.column_stack(features)
        
        # Handle infinite values
        X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
        
        return X
    
    def train_isolation_forest(self, training_data: pd.DataFrame, contamination: float = 0.1) -> Dict:
        """Train Isolation Forest for anomaly detection"""
        X = self.prepare_features(training_data)
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        self.model.fit(X_scaled)
        
        # Calculate training metrics
        predictions = self.model.predict(X_scaled)
        anomaly_ratio = np.sum(predictions == -1) / len(predictions)
        
        logger.info(f"Isolation Forest trained with anomaly ratio: {anomaly_ratio:.3f}")
        
        return {
            "model_type": "isolation_forest",
            "anomaly_ratio": anomaly_ratio,
            "n_samples": len(X),
            "contamination": contamination
        }
    
    def train_lstm_autoencoder(self, training_data: pd.DataFrame, sequence_length: int = 10) -> Dict:
        """Train LSTM Autoencoder for anomaly detection"""
        X = self.prepare_features(training_data)
        X_scaled = self.scaler.fit_transform(X)
        
        # Create sequences
        X_sequences = self._create_sequences(X_scaled, sequence_length)
        
        # Build LSTM Autoencoder
        model = Sequential([
            LSTM(64, activation='relu', input_shape=(sequence_length, X_scaled.shape[1]), return_sequences=True),
            Dropout(0.2),
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(64, activation='relu'),
            Dense(X_scaled.shape[1])
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train the model
        history = model.fit(
            X_sequences, X_sequences[:, -1, :],
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        self.model = model
        
        # Calculate reconstruction threshold
        predictions = model.predict(X_sequences)
        mse = np.mean(np.power(X_sequences[:, -1, :] - predictions, 2), axis=1)
        self.threshold = np.percentile(mse, 95)
        
        logger.info(f"LSTM Autoencoder trained with threshold: {self.threshold:.6f}")
        
        return {
            "model_type": "lstm_autoencoder",
            "threshold": self.threshold,
            "final_loss": history.history['loss'][-1],
            "n_samples": len(X_sequences)
        }
    
    def detect_anomalies(self, data: pd.DataFrame) -> Dict:
        """Detect anomalies in network traffic"""
        if self.model is None:
            return {"error": "Model not trained"}
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        if self.model_type == "isolation_forest":
            predictions = self.model.predict(X_scaled)
            anomaly_scores = self.model.decision_function(X_scaled)
            
            # Convert predictions (-1 for anomaly, 1 for normal)
            is_anomaly = predictions == -1
            
        elif self.model_type == "lstm_autoencoder":
            if len(X_scaled) < 10:  # Need minimum sequence length
                return {"anomalies": [], "anomaly_count": 0}
            
            sequences = self._create_sequences(X_scaled, 10)
            predictions = self.model.predict(sequences)
            
            # Calculate reconstruction error
            mse = np.mean(np.power(sequences[:, -1, :] - predictions, 2), axis=1)
            is_anomaly = mse > self.threshold
            anomaly_scores = mse
        
        else:
            return {"error": f"Unknown model type: {self.model_type}"}
        
        # Prepare results
        anomaly_indices = np.where(is_anomaly)[0].tolist()
        anomaly_count = len(anomaly_indices)
        
        results = {
            "anomaly_count": anomaly_count,
            "total_samples": len(data),
            "anomaly_ratio": anomaly_count / len(data) if len(data) > 0 else 0,
            "anomaly_indices": anomaly_indices,
            "anomaly_scores": anomaly_scores.tolist() if hasattr(anomaly_scores, 'tolist') else anomaly_scores
        }
        
        # Add detailed anomaly information
        if anomaly_count > 0:
            anomaly_data = data.iloc[anomaly_indices].copy()
            anomaly_data['anomaly_score'] = [anomaly_scores[i] for i in anomaly_indices]
            results["anomalies"] = anomaly_data.to_dict('records')
        else:
            results["anomalies"] = []
        
        return results
    
    def _create_sequences(self, data: np.ndarray, sequence_length: int) -> np.ndarray:
        """Create sequences for LSTM input"""
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:i + sequence_length])
        return np.array(sequences)
    
    def evaluate_model(self, test_data: pd.DataFrame, true_labels: np.ndarray) -> Dict:
        """Evaluate anomaly detection model"""
        results = self.detect_anomalies(test_data)
        
        if "error" in results:
            return results
        
        # Create binary predictions
        predictions = np.zeros(len(test_data))
        if results["anomaly_indices"]:
            predictions[results["anomaly_indices"]] = 1
        
        # Calculate metrics
        from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
        
        accuracy = accuracy_score(true_labels, predictions)
        precision = precision_score(true_labels, predictions, zero_division=0)
        recall = recall_score(true_labels, predictions, zero_division=0)
        f1 = f1_score(true_labels, predictions, zero_division=0)
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "predicted_anomalies": int(np.sum(predictions)),
            "actual_anomalies": int(np.sum(true_labels))
        }
    
    def save_model(self, filepath: str):
        """Save trained model"""
        model_data = {
            "model_type": self.model_type,
            "scaler": self.scaler,
            "feature_columns": self.feature_columns,
            "threshold": self.threshold
        }
        
        if self.model_type == "isolation_forest":
            model_data["model"] = self.model
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
        
        elif self.model_type == "lstm_autoencoder":
            # Save Keras model separately
            self.model.save(filepath.replace('.pkl', '.h5'))
            # Save other data
            with open(filepath, 'wb') as f:
                pickle.dump({k: v for k, v in model_data.items() if k != "model"}, f)
        
        logger.info(f"Anomaly detection model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model_type = model_data["model_type"]
            self.scaler = model_data["scaler"]
            self.feature_columns = model_data["feature_columns"]
            self.threshold = model_data["threshold"]
            
            if self.model_type == "isolation_forest":
                self.model = model_data["model"]
            elif self.model_type == "lstm_autoencoder":
                self.model = tf.keras.models.load_model(filepath.replace('.pkl', '.h5'))
            
            logger.info(f"Anomaly detection model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise