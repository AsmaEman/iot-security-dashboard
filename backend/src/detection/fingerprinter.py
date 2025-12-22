import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import pickle
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class DeviceFingerprinter:
    """Device fingerprinting using network traffic patterns"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.device_profiles = {}
        self.feature_columns = [
            'packet_size_mean', 'packet_size_std', 'inter_arrival_mean',
            'inter_arrival_std', 'port_entropy', 'protocol_diversity',
            'bytes_per_second', 'packets_per_second'
        ]
        
        if model_path:
            self.load_model(model_path)
    
    def extract_device_features(self, traffic_data: pd.DataFrame) -> Dict:
        """Extract device fingerprinting features from network traffic"""
        features = {}
        
        if traffic_data.empty:
            return {col: 0.0 for col in self.feature_columns}
        
        # Packet size statistics
        if 'packet_size' in traffic_data.columns:
            features['packet_size_mean'] = traffic_data['packet_size'].mean()
            features['packet_size_std'] = traffic_data['packet_size'].std()
        else:
            features['packet_size_mean'] = 0.0
            features['packet_size_std'] = 0.0
        
        # Inter-arrival time statistics
        if 'timestamp' in traffic_data.columns:
            traffic_data['timestamp'] = pd.to_datetime(traffic_data['timestamp'])
            inter_arrivals = traffic_data['timestamp'].diff().dt.total_seconds().dropna()
            features['inter_arrival_mean'] = inter_arrivals.mean() if not inter_arrivals.empty else 0.0
            features['inter_arrival_std'] = inter_arrivals.std() if not inter_arrivals.empty else 0.0
        else:
            features['inter_arrival_mean'] = 0.0
            features['inter_arrival_std'] = 0.0
        
        # Port entropy
        if 'dst_port' in traffic_data.columns:
            port_counts = traffic_data['dst_port'].value_counts()
            port_probs = port_counts / port_counts.sum()
            features['port_entropy'] = -np.sum(port_probs * np.log2(port_probs + 1e-10))
        else:
            features['port_entropy'] = 0.0
        
        # Protocol diversity
        if 'protocol' in traffic_data.columns:
            features['protocol_diversity'] = traffic_data['protocol'].nunique()
        else:
            features['protocol_diversity'] = 0.0
        
        # Traffic rate features
        if 'timestamp' in traffic_data.columns and not traffic_data.empty:
            duration = (traffic_data['timestamp'].max() - traffic_data['timestamp'].min()).total_seconds()
            if duration > 0:
                total_bytes = traffic_data.get('packet_size', pd.Series([0])).sum()
                total_packets = len(traffic_data)
                features['bytes_per_second'] = total_bytes / duration
                features['packets_per_second'] = total_packets / duration
            else:
                features['bytes_per_second'] = 0.0
                features['packets_per_second'] = 0.0
        else:
            features['bytes_per_second'] = 0.0
            features['packets_per_second'] = 0.0
        
        return features
    
    def train_fingerprinter(self, training_data: List[Tuple[pd.DataFrame, str]]) -> Dict:
        """Train device fingerprinting model"""
        X = []
        y = []
        
        for traffic_data, device_type in training_data:
            features = self.extract_device_features(traffic_data)
            feature_vector = [features.get(col, 0.0) for col in self.feature_columns]
            X.append(feature_vector)
            y.append(device_type)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest classifier
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Calculate training metrics
        train_accuracy = self.model.score(X_scaled, y)
        
        logger.info(f"Device fingerprinter trained with accuracy: {train_accuracy:.3f}")
        
        return {
            "accuracy": train_accuracy,
            "n_samples": len(X),
            "n_features": len(self.feature_columns),
            "device_types": list(set(y))
        }
    
    def identify_device(self, traffic_data: pd.DataFrame) -> Dict:
        """Identify device type from network traffic"""
        if self.model is None:
            return {"device_type": "unknown", "confidence": 0.0}
        
        features = self.extract_device_features(traffic_data)
        feature_vector = np.array([[features.get(col, 0.0) for col in self.feature_columns]])
        
        # Scale features
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Predict device type
        prediction = self.model.predict(feature_vector_scaled)[0]
        probabilities = self.model.predict_proba(feature_vector_scaled)[0]
        confidence = np.max(probabilities)
        
        return {
            "device_type": prediction,
            "confidence": float(confidence),
            "features": features
        }
    
    def create_device_profile(self, device_id: str, traffic_data: pd.DataFrame) -> Dict:
        """Create behavioral profile for a device"""
        features = self.extract_device_features(traffic_data)
        
        profile = {
            "device_id": device_id,
            "profile_created": pd.Timestamp.now().isoformat(),
            "traffic_samples": len(traffic_data),
            "behavioral_features": features,
            "baseline_established": True
        }
        
        self.device_profiles[device_id] = profile
        return profile
    
    def detect_profile_deviation(self, device_id: str, current_traffic: pd.DataFrame, threshold: float = 0.3) -> Dict:
        """Detect deviation from established device profile"""
        if device_id not in self.device_profiles:
            return {"deviation_detected": False, "reason": "No baseline profile"}
        
        baseline_features = self.device_profiles[device_id]["behavioral_features"]
        current_features = self.extract_device_features(current_traffic)
        
        # Calculate feature deviations
        deviations = {}
        total_deviation = 0.0
        
        for feature in self.feature_columns:
            baseline_val = baseline_features.get(feature, 0.0)
            current_val = current_features.get(feature, 0.0)
            
            if baseline_val != 0:
                deviation = abs(current_val - baseline_val) / baseline_val
            else:
                deviation = abs(current_val)
            
            deviations[feature] = deviation
            total_deviation += deviation
        
        avg_deviation = total_deviation / len(self.feature_columns)
        deviation_detected = avg_deviation > threshold
        
        return {
            "deviation_detected": deviation_detected,
            "average_deviation": avg_deviation,
            "threshold": threshold,
            "feature_deviations": deviations,
            "severity": "high" if avg_deviation > 0.5 else "medium" if avg_deviation > 0.3 else "low"
        }
    
    def save_model(self, filepath: str):
        """Save trained model and scaler"""
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_columns": self.feature_columns,
            "device_profiles": self.device_profiles
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Device fingerprinter model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model and scaler"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.feature_columns = model_data["feature_columns"]
            self.device_profiles = model_data.get("device_profiles", {})
            
            logger.info(f"Device fingerprinter model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise