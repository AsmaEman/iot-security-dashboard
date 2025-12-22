import pandas as pd
import numpy as np
from typing import Dict, List
from .dataset_processor import BaseDatasetProcessor
import logging

logger = logging.getLogger(__name__)

class TONIoTProcessor(BaseDatasetProcessor):
    """Processor for TON-IoT dataset"""
    
    def __init__(self, dataset_path: str):
        super().__init__(dataset_path)
        self.feature_columns = [
            'ts', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto',
            'duration', 'src_bytes', 'dst_bytes', 'src_pkts', 'dst_pkts',
            'src_ip_bytes', 'dst_ip_bytes'
        ]
        
    def load_data(self) -> pd.DataFrame:
        """Load TON-IoT dataset"""
        try:
            # TON-IoT dataset is typically in CSV format
            self.data = pd.read_csv(self.dataset_path)
            logger.info(f"Loaded TON-IoT dataset with shape: {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading TON-IoT dataset: {e}")
            raise
    
    def preprocess(self) -> pd.DataFrame:
        """Preprocess TON-IoT dataset"""
        if self.data is None:
            self.load_data()
        
        df = self.data.copy()
        
        # Convert timestamp
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
        
        # Handle IP addresses - convert to numeric representation
        if 'src_ip' in df.columns:
            df['src_ip_numeric'] = df['src_ip'].apply(self._ip_to_int)
        if 'dst_ip' in df.columns:
            df['dst_ip_numeric'] = df['dst_ip'].apply(self._ip_to_int)
        
        # Clean data
        df = self.clean_data(df)
        
        # Create binary labels for anomaly detection
        if 'label' in df.columns:
            df['is_anomaly'] = (df['label'] != 'normal').astype(int)
        
        self.processed_data = df
        logger.info(f"Preprocessed TON-IoT dataset with shape: {df.shape}")
        return df
    
    def extract_features(self) -> pd.DataFrame:
        """Extract features for ML models"""
        if self.processed_data is None:
            self.preprocess()
        
        df = self.processed_data.copy()
        
        # Network flow features
        df['bytes_ratio'] = df['src_bytes'] / (df['dst_bytes'] + 1)
        df['pkts_ratio'] = df['src_pkts'] / (df['dst_pkts'] + 1)
        df['bytes_per_pkt_src'] = df['src_bytes'] / (df['src_pkts'] + 1)
        df['bytes_per_pkt_dst'] = df['dst_bytes'] / (df['dst_pkts'] + 1)
        
        # Time-based features
        if 'ts' in df.columns:
            df['hour'] = df['ts'].dt.hour
            df['day_of_week'] = df['ts'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Protocol encoding
        if 'proto' in df.columns:
            df = self.encode_categorical(df, ['proto'])
        
        # Select feature columns for ML
        feature_cols = [
            'src_port', 'dst_port', 'proto', 'duration',
            'src_bytes', 'dst_bytes', 'src_pkts', 'dst_pkts',
            'bytes_ratio', 'pkts_ratio', 'bytes_per_pkt_src', 'bytes_per_pkt_dst',
            'hour', 'day_of_week', 'is_weekend'
        ]
        
        # Filter existing columns
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Normalize features
        df = self.normalize_features(df, feature_cols)
        
        logger.info(f"Extracted {len(feature_cols)} features from TON-IoT dataset")
        return df
    
    def _ip_to_int(self, ip_str: str) -> int:
        """Convert IP address string to integer"""
        try:
            if pd.isna(ip_str):
                return 0
            parts = ip_str.split('.')
            return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
        except:
            return 0
    
    def get_attack_distribution(self) -> Dict:
        """Get distribution of attack types"""
        if self.processed_data is None:
            return {}
        
        if 'label' in self.processed_data.columns:
            return self.processed_data['label'].value_counts().to_dict()
        return {}
    
    def get_protocol_distribution(self) -> Dict:
        """Get distribution of protocols"""
        if self.processed_data is None:
            return {}
        
        if 'proto' in self.processed_data.columns:
            return self.processed_data['proto'].value_counts().to_dict()
        return {}