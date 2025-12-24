import asyncio
import uuid
from typing import Dict, Any
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class MockTask:
    """Mock Celery task for development"""
    
    def __init__(self, task_id: str = None):
        self.id = task_id or str(uuid.uuid4())
    
    def delay(self, *args, **kwargs):
        """Mock delay method"""
        logger.info(f"Mock task {self.id} started with args: {args}, kwargs: {kwargs}")
        return self

# Mock scan device task
scan_device_task = MockTask()