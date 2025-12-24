from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# API Metrics
API_REQUESTS = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

API_REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# Device Metrics
DEVICE_COUNT = Gauge(
    'devices_total',
    'Total number of devices'
)

DEVICE_IDENTIFICATION_ACCURACY = Gauge(
    'device_identification_accuracy',
    'Device identification accuracy'
)

DEVICE_FINGERPRINTING_DURATION = Histogram(
    'device_fingerprinting_duration_seconds',
    'Time taken for device fingerprinting'
)

# Alert Metrics
ALERT_COUNT = Gauge(
    'alerts_total',
    'Total number of alerts',
    ['severity', 'status']
)

ALERTS_GENERATED = Counter(
    'alerts_generated_total',
    'Total alerts generated',
    ['alert_type', 'severity']
)

# Anomaly Detection Metrics
ANOMALY_DETECTION_ACCURACY = Gauge(
    'anomaly_detection_accuracy',
    'Anomaly detection accuracy'
)

ANOMALY_DETECTION_LATENCY = Histogram(
    'anomaly_detection_latency_seconds',
    'Time taken for anomaly detection',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

ANOMALIES_DETECTED = Counter(
    'anomalies_detected_total',
    'Total anomalies detected',
    ['anomaly_type']
)

# ML Model Metrics
ML_MODEL_ACCURACY = Gauge(
    'ml_model_accuracy',
    'ML model accuracy',
    ['model_name', 'model_type']
)

ML_INFERENCE_DURATION = Histogram(
    'ml_inference_duration_seconds',
    'ML model inference time',
    ['model_name']
)

ML_PREDICTIONS = Counter(
    'ml_predictions_total',
    'Total ML predictions made',
    ['model_name', 'prediction_type']
)

# Database Metrics
DB_CONNECTIONS = Gauge(
    'database_connections_active',
    'Active database connections'
)

DB_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# System Metrics
SYSTEM_INFO = Info(
    'system_info',
    'System information'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

# WebSocket Metrics
WEBSOCKET_CONNECTIONS = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections'
)

WEBSOCKET_MESSAGES = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['message_type']
)

# Dataset Processing Metrics
DATASET_PROCESSING_DURATION = Histogram(
    'dataset_processing_duration_seconds',
    'Dataset processing time',
    ['dataset_name']
)

DATASET_SAMPLES_PROCESSED = Counter(
    'dataset_samples_processed_total',
    'Total dataset samples processed',
    ['dataset_name']
)

# Vulnerability Metrics
VULNERABILITIES_FOUND = Counter(
    'vulnerabilities_found_total',
    'Total vulnerabilities found',
    ['severity', 'cve_type']
)

CVE_LOOKUP_DURATION = Histogram(
    'cve_lookup_duration_seconds',
    'CVE lookup duration'
)

# Decorator for timing functions
def time_function(metric: Histogram):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric.observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric.observe(duration)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Metrics collection class
class MetricsCollector:
    """Centralized metrics collection"""
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        API_REQUESTS.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        API_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def update_device_count(count: int):
        """Update device count metric"""
        DEVICE_COUNT.set(count)
    
    @staticmethod
    def record_device_identification(accuracy: float, duration: float):
        """Record device identification metrics"""
        DEVICE_IDENTIFICATION_ACCURACY.set(accuracy)
        DEVICE_FINGERPRINTING_DURATION.observe(duration)
    
    @staticmethod
    def record_alert(alert_type: str, severity: str):
        """Record alert generation"""
        ALERTS_GENERATED.labels(alert_type=alert_type, severity=severity).inc()
    
    @staticmethod
    def update_alert_counts(severity_counts: dict, status_counts: dict):
        """Update alert count metrics"""
        for severity, count in severity_counts.items():
            for status, status_count in status_counts.items():
                ALERT_COUNT.labels(severity=severity, status=status).set(status_count)
    
    @staticmethod
    def record_anomaly_detection(accuracy: float, latency: float, anomaly_type: str):
        """Record anomaly detection metrics"""
        ANOMALY_DETECTION_ACCURACY.set(accuracy)
        ANOMALY_DETECTION_LATENCY.observe(latency)
        ANOMALIES_DETECTED.labels(anomaly_type=anomaly_type).inc()
    
    @staticmethod
    def record_ml_prediction(model_name: str, prediction_type: str, duration: float):
        """Record ML prediction metrics"""
        ML_PREDICTIONS.labels(model_name=model_name, prediction_type=prediction_type).inc()
        ML_INFERENCE_DURATION.labels(model_name=model_name).observe(duration)
    
    @staticmethod
    def update_ml_model_accuracy(model_name: str, model_type: str, accuracy: float):
        """Update ML model accuracy"""
        ML_MODEL_ACCURACY.labels(model_name=model_name, model_type=model_type).set(accuracy)
    
    @staticmethod
    def record_websocket_connection(active_connections: int):
        """Record WebSocket connection metrics"""
        WEBSOCKET_CONNECTIONS.set(active_connections)
    
    @staticmethod
    def record_websocket_message(message_type: str):
        """Record WebSocket message"""
        WEBSOCKET_MESSAGES.labels(message_type=message_type).inc()

# Initialize system info
SYSTEM_INFO.info({
    'version': '2.0.0',
    'service': 'iot-security-dashboard',
    'component': 'backend'
})

# Export metrics instance
METRICS = MetricsCollector()