import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseDatasetProcessor(ABC):
    """Base class for dataset processors"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Load raw dataset"""
        pass
    
    @abstractmethod
    def preprocess(self) -> pd.DataFrame:
        """Preprocess the dataset"""
        pass
    
    @abstractmethod
    def extract_features(self) -> pd.DataFrame:
        """Extract relevant features"""
        pass
    
    def get_data_info(self) -> Dict:
        """Get dataset information"""
        if self.data is None:
            return {}
            
        return {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "memory_usage": self.data.memory_usage(deep=True).sum()
        }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Common data cleaning operations"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # Fill numeric missing values with median
        for col in numeric_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical missing values with mode
        for col in categorical_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown', inplace=True)
        
        return df
    
    def normalize_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize specified columns"""
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        df[columns] = scaler.fit_transform(df[columns])
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Encode categorical variables"""
        from sklearn.preprocessing import LabelEncoder
        
        for col in columns:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
        
        return df