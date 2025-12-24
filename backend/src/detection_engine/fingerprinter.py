import asyncio
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

from ..utils.logger import setup_logger
from ..utils.metrics import time_function, DEVICE_FINGERPRINTING_DURATION

logger = setup_logger(__name__)

@dataclass
class FingerprintSignature:
    """Container for device fingerprint signatures"""
    dhcp_options: Dict[str, Any]
    tls_ja3: Optional[str]
    http_user_agent: Optional[str]
    behavioral_patterns: Dict[str, float]
    network_stats: Dict[str, float]

class DeviceFingerprinter:
    """Advanced device fingerprinting using multiple signatures"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "/app/ml_models/device_fingerprinter.pkl"
        self.scaler = StandardScaler()
        self.classifier = None
        self.device_signatures = {}
        self.confidence_threshold = 0.8
        
        # Device type mappings
        self.device_types = [
            "Security Camera", "Smart Thermostat", "Smart Lock", "Motion Sensor",
            "Smart Hub", "Router", "Switch", "Access Point", "Printer",
            "Smart TV", "Gaming Console", "Smartphone", "Tablet", "Laptop",
            "Desktop", "Server", "IoT Sensor", "Industrial PLC", "HMI",
            "Smart Speaker", "Smart Light", "Smart Plug", "Unknown"
        ]
        
        # Vendor mappings
        self.vendors = [
            "Nest", "Ring", "August", "Philips", "Samsung", "Cisco",
            "Netgear", "TP-Link", "HP", "Canon", "Sony", "Apple",
            "Microsoft", "Google", "Amazon", "Siemens", "Schneider Electric",
            "Unknown"
        ]
        
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.classifier = model_data['classifier']
                    self.scaler = model_data['scaler']
                    logger.info("Device fingerprinting model loaded successfully")
            else:
                self._create_mock_model()
                logger.info("Created mock device fingerprinting model")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration"""
        # Generate synthetic training data
        n_samples = 1000
        n_features = 45
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice(len(self.device_types), n_samples)
        
        # Train model
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.classifier.fit(X_scaled, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'classifier': self.classifier,
                'scaler': self.scaler
            }, f)
    
    @time_function(DEVICE_FINGERPRINTING_DURATION)
    async def fingerprint_device(self, ip_address: str) -> Dict[str, Any]:
        """Perform comprehensive device fingerprinting"""
        
        start_time = time.time()
        
        try:
            # Extract signatures (mock implementation)
            signatures = await self._extract_signatures(ip_address)
            
            # Perform ML-based classification
            classification = await self._classify_device(signatures)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(signatures, classification)
            
            # Generate fingerprint result
            result = {
                "device_type": classification["device_type"],
                "vendor": classification["vendor"],
                "confidence": confidence,
                "dhcp_fingerprint": signatures.dhcp_options,
                "tls_fingerprint": {"ja3": signatures.tls_ja3} if signatures.tls_ja3 else None,
                "http_fingerprint": {"user_agent": signatures.http_user_agent} if signatures.http_user_agent else None,
                "behavioral_fingerprint": signatures.behavioral_patterns,
                "contributing_factors": classification["contributing_factors"],
                "processing_time": time.time() - start_time
            }
            
            logger.info(f"Device fingerprinting completed for {ip_address}: {classification['device_type']} ({confidence:.2f} confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Fingerprinting failed for {ip_address}: {e}")
            return {
                "device_type": "Unknown",
                "vendor": "Unknown",
                "confidence": 0.0,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _extract_signatures(self, ip_address: str) -> FingerprintSignature:
        """Extract device signatures from network traffic"""
        
        # Mock signature extraction (in real implementation, this would analyze actual traffic)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Generate realistic mock signatures
        dhcp_options = self._generate_mock_dhcp_signature()
        tls_ja3 = self._generate_mock_tls_signature()
        http_user_agent = self._generate_mock_http_signature()
        behavioral_patterns = self._generate_mock_behavioral_signature()
        network_stats = self._generate_mock_network_stats()
        
        return FingerprintSignature(
            dhcp_options=dhcp_options,
            tls_ja3=tls_ja3,
            http_user_agent=http_user_agent,
            behavioral_patterns=behavioral_patterns,
            network_stats=network_stats
        )
    
    def _generate_mock_dhcp_signature(self) -> Dict[str, Any]:
        """Generate mock DHCP signature"""
        dhcp_signatures = [
            {
                "hostname": "SecurityCamera-001",
                "vendor_class": "Hikvision",
                "parameter_request_list": [1, 3, 6, 15, 31, 33, 43, 44, 46, 47, 119, 121, 249, 252],
                "fingerprint_confidence": 0.9
            },
            {
                "hostname": "Nest-Thermostat",
                "vendor_class": "Google Nest",
                "parameter_request_list": [1, 3, 6, 15, 26, 28, 51, 58, 59, 43],
                "fingerprint_confidence": 0.95
            },
            {
                "hostname": "SmartHub-Samsung",
                "vendor_class": "Samsung SmartThings",
                "parameter_request_list": [1, 3, 6, 15, 31, 33, 43, 44, 46, 47],
                "fingerprint_confidence": 0.88
            }
        ]
        
        return random.choice(dhcp_signatures)
    
    def _generate_mock_tls_signature(self) -> Optional[str]:
        """Generate mock TLS JA3 signature"""
        ja3_signatures = [
            "769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0",
            "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0",
            "772,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172,65281-0-23-35-13-5-18-16-30-27-43,29-23-24-25-256-257,0"
        ]
        
        return random.choice(ja3_signatures) if random.random() > 0.3 else None
    
    def _generate_mock_http_signature(self) -> Optional[str]:
        """Generate mock HTTP User-Agent signature"""
        user_agents = [
            "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Nest/5.9.3 (iPhone; iOS 14.6; Scale/3.00)",
            "Samsung SmartThings Hub/2.1.4",
            "Ring/3.21.1 (Android 9; SM-G960F)",
            "Philips Hue Bridge/1.45.0"
        ]
        
        return random.choice(user_agents) if random.random() > 0.4 else None
    
    def _generate_mock_behavioral_signature(self) -> Dict[str, float]:
        """Generate mock behavioral patterns"""
        return {
            "avg_packet_size": random.uniform(200, 1500),
            "packets_per_second": random.uniform(0.1, 10.0),
            "connection_frequency": random.uniform(0.01, 1.0),
            "protocol_diversity": random.uniform(0.1, 0.8),
            "port_entropy": random.uniform(1.0, 4.0),
            "daily_pattern_score": random.uniform(0.3, 0.9),
            "periodic_behavior": random.uniform(0.2, 0.8)
        }
    
    def _generate_mock_network_stats(self) -> Dict[str, float]:
        """Generate mock network statistics"""
        return {
            "bytes_per_second": random.uniform(100, 10000),
            "unique_destinations": random.randint(1, 50),
            "tcp_ratio": random.uniform(0.6, 0.9),
            "udp_ratio": random.uniform(0.1, 0.3),
            "icmp_ratio": random.uniform(0.0, 0.1)
        }
    
    async def _classify_device(self, signatures: FingerprintSignature) -> Dict[str, Any]:
        """Classify device using ML model"""
        
        # Extract features for ML model
        features = self._extract_ml_features(signatures)
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Predict device type
        prediction = self.classifier.predict(features_scaled)[0]
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        
        # Get feature importance for explainability
        feature_importance = self.classifier.feature_importances_
        
        device_type = self.device_types[prediction]
        vendor = self._infer_vendor(signatures, device_type)
        
        return {
            "device_type": device_type,
            "vendor": vendor,
            "prediction_probabilities": probabilities.tolist(),
            "contributing_factors": {
                "dhcp_signature": 0.4 if signatures.dhcp_options else 0.0,
                "tls_signature": 0.3 if signatures.tls_ja3 else 0.0,
                "http_signature": 0.2 if signatures.http_user_agent else 0.0,
                "behavioral_patterns": 0.1
            }
        }
    
    def _extract_ml_features(self, signatures: FingerprintSignature) -> List[float]:
        """Extract numerical features for ML model"""
        features = []
        
        # DHCP features (15 features)
        dhcp = signatures.dhcp_options
        features.extend([
            len(dhcp.get("parameter_request_list", [])),
            1.0 if dhcp.get("hostname") else 0.0,
            1.0 if dhcp.get("vendor_class") else 0.0,
            dhcp.get("fingerprint_confidence", 0.0),
            # Add more DHCP-derived features
            *[random.uniform(0, 1) for _ in range(11)]
        ])
        
        # TLS features (10 features)
        features.extend([
            1.0 if signatures.tls_ja3 else 0.0,
            len(signatures.tls_ja3.split(',')[1].split('-')) if signatures.tls_ja3 else 0,
            # Add more TLS-derived features
            *[random.uniform(0, 1) for _ in range(8)]
        ])
        
        # HTTP features (5 features)
        features.extend([
            1.0 if signatures.http_user_agent else 0.0,
            len(signatures.http_user_agent) if signatures.http_user_agent else 0,
            # Add more HTTP-derived features
            *[random.uniform(0, 1) for _ in range(3)]
        ])
        
        # Behavioral features (10 features)
        behavioral = signatures.behavioral_patterns
        features.extend([
            behavioral.get("avg_packet_size", 0) / 1500,  # Normalize
            behavioral.get("packets_per_second", 0) / 10,
            behavioral.get("connection_frequency", 0),
            behavioral.get("protocol_diversity", 0),
            behavioral.get("port_entropy", 0) / 4,
            behavioral.get("daily_pattern_score", 0),
            behavioral.get("periodic_behavior", 0),
            *[random.uniform(0, 1) for _ in range(3)]
        ])
        
        # Network statistics features (5 features)
        network = signatures.network_stats
        features.extend([
            network.get("bytes_per_second", 0) / 10000,  # Normalize
            network.get("unique_destinations", 0) / 50,
            network.get("tcp_ratio", 0),
            network.get("udp_ratio", 0),
            network.get("icmp_ratio", 0)
        ])
        
        return features[:45]  # Ensure exactly 45 features
    
    def _infer_vendor(self, signatures: FingerprintSignature, device_type: str) -> str:
        """Infer vendor from signatures and device type"""
        
        # Check DHCP vendor class
        if signatures.dhcp_options.get("vendor_class"):
            vendor_class = signatures.dhcp_options["vendor_class"].lower()
            for vendor in self.vendors:
                if vendor.lower() in vendor_class:
                    return vendor
        
        # Check hostname patterns
        if signatures.dhcp_options.get("hostname"):
            hostname = signatures.dhcp_options["hostname"].lower()
            vendor_patterns = {
                "nest": "Nest",
                "ring": "Ring",
                "samsung": "Samsung",
                "philips": "Philips",
                "cisco": "Cisco",
                "netgear": "Netgear"
            }
            
            for pattern, vendor in vendor_patterns.items():
                if pattern in hostname:
                    return vendor
        
        # Check User-Agent
        if signatures.http_user_agent:
            ua = signatures.http_user_agent.lower()
            for vendor in self.vendors:
                if vendor.lower() in ua:
                    return vendor
        
        # Default vendor inference based on device type
        device_vendor_mapping = {
            "Security Camera": random.choice(["Hikvision", "Dahua", "Axis", "Ring"]),
            "Smart Thermostat": random.choice(["Nest", "Honeywell", "Ecobee"]),
            "Smart Hub": random.choice(["Samsung", "Philips", "Amazon"]),
            "Router": random.choice(["Cisco", "Netgear", "TP-Link"]),
            "Smart Speaker": random.choice(["Amazon", "Google", "Apple"])
        }
        
        return device_vendor_mapping.get(device_type, "Unknown")
    
    def _calculate_confidence(self, signatures: FingerprintSignature, classification: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        
        confidence_factors = []
        
        # DHCP confidence
        if signatures.dhcp_options:
            dhcp_conf = signatures.dhcp_options.get("fingerprint_confidence", 0.5)
            confidence_factors.append(dhcp_conf * 0.4)
        
        # TLS confidence
        if signatures.tls_ja3:
            confidence_factors.append(0.8 * 0.3)  # High confidence for TLS fingerprints
        
        # HTTP confidence
        if signatures.http_user_agent:
            confidence_factors.append(0.7 * 0.2)  # Medium confidence for User-Agent
        
        # Behavioral confidence
        behavioral_score = np.mean(list(signatures.behavioral_patterns.values()))
        confidence_factors.append(min(behavioral_score, 1.0) * 0.1)
        
        # ML model confidence
        max_prob = max(classification["prediction_probabilities"])
        confidence_factors.append(max_prob)
        
        # Calculate weighted average
        if confidence_factors:
            final_confidence = np.mean(confidence_factors)
            return min(final_confidence, 1.0)
        
        return 0.5  # Default confidence
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the fingerprinting model"""
        return {
            "model_type": "Random Forest Ensemble",
            "features": 45,
            "device_types": len(self.device_types),
            "vendors": len(self.vendors),
            "confidence_threshold": self.confidence_threshold,
            "model_path": self.model_path
        }