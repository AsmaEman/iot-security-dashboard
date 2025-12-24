from typing import Dict, Any
import time
from datetime import datetime

class MetricsCollector:
    """Simple metrics collector for development"""
    
    def __init__(self):
        self.metrics = {
            "device_count": 0,
            "alert_count": 0,
            "identification_accuracy": [],
            "processing_times": [],
            "start_time": time.time()
        }
    
    def update_device_count(self, count: int):
        """Update device count metric"""
        self.metrics["device_count"] = count
    
    def update_alert_count(self, count: int):
        """Update alert count metric"""
        self.metrics["alert_count"] = count
    
    def record_device_identification(self, accuracy: float, processing_time: float):
        """Record device identification metrics"""
        self.metrics["identification_accuracy"].append(accuracy)
        self.metrics["processing_times"].append(processing_time)
        
        # Keep only last 1000 records
        if len(self.metrics["identification_accuracy"]) > 1000:
            self.metrics["identification_accuracy"] = self.metrics["identification_accuracy"][-1000:]
        if len(self.metrics["processing_times"]) > 1000:
            self.metrics["processing_times"] = self.metrics["processing_times"][-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.metrics["start_time"]
        
        avg_accuracy = 0.0
        if self.metrics["identification_accuracy"]:
            avg_accuracy = sum(self.metrics["identification_accuracy"]) / len(self.metrics["identification_accuracy"])
        
        avg_processing_time = 0.0
        if self.metrics["processing_times"]:
            avg_processing_time = sum(self.metrics["processing_times"]) / len(self.metrics["processing_times"])
        
        return {
            "device_count": self.metrics["device_count"],
            "alert_count": self.metrics["alert_count"],
            "avg_identification_accuracy": round(avg_accuracy, 3),
            "avg_processing_time": round(avg_processing_time, 3),
            "uptime_seconds": round(uptime, 1),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global metrics instance
METRICS = MetricsCollector()