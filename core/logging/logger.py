"""
Advanced Logging System
Auto-cleanup of logs older than configured days
Logs organized by type, method, date, and time
"""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import json

from core.config import settings


class CustomLogger:
    """
    Custom logger with automatic file organization and cleanup
    """
    
    def __init__(self, name: str, log_type: str = "application"):
        """
        Initialize logger
        
        Args:
            name: Logger name
            log_type: Type of log (application, security, database, etc.)
        """
        self.name = name
        self.log_type = log_type
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _get_log_file_path(self, method: Optional[str] = None) -> str:
        """
        Get log file path organized by type, date, and optionally method
        
        Args:
            method: HTTP method or operation type
            
        Returns:
            str: Full path to log file
        """
        # Base logs directory
        logs_dir = Path("logs")
        
        # Organize by type
        type_dir = logs_dir / self.log_type
        
        # Organize by date
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = type_dir / current_date
        
        # Create directories if they don't exist
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with method if provided
        if method:
            filename = f"{self.name}_{method}_{datetime.now().strftime('%H')}.log"
        else:
            filename = f"{self.name}_{datetime.now().strftime('%H')}.log"
        
        return str(date_dir / filename)
    
    def _write_to_file(self, level: str, message: str, method: Optional[str] = None, 
                       extra_info: Optional[Dict] = None):
        """Write log entry to file"""
        log_file = self._get_log_file_path(method)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "type": self.log_type,
            "method": method,
            "message": message,
            "extra_info": extra_info or {}
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def info(self, message: str, method: Optional[str] = None, extra_info: Optional[Dict] = None):
        """Log info level message"""
        self.logger.info(message)
        self._write_to_file("INFO", message, method, extra_info)
    
    def warning(self, message: str, method: Optional[str] = None, extra_info: Optional[Dict] = None):
        """Log warning level message"""
        self.logger.warning(message)
        self._write_to_file("WARNING", message, method, extra_info)
    
    def error(self, message: str, method: Optional[str] = None, extra_info: Optional[Dict] = None):
        """Log error level message"""
        self.logger.error(message)
        self._write_to_file("ERROR", message, method, extra_info)
    
    def critical(self, message: str, method: Optional[str] = None, extra_info: Optional[Dict] = None):
        """Log critical level message"""
        self.logger.critical(message)
        self._write_to_file("CRITICAL", message, method, extra_info)
    
    def debug(self, message: str, method: Optional[str] = None, extra_info: Optional[Dict] = None):
        """Log debug level message"""
        self.logger.debug(message)
        self._write_to_file("DEBUG", message, method, extra_info)


def cleanup_old_logs(days: int = None):
    """
    Delete log files older than specified days
    
    Args:
        days: Number of days to retain logs (default from settings)
    """
    if days is None:
        days = settings.LOG_RETENTION_DAYS
    
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    try:
        # Iterate through all log type directories
        for type_dir in logs_dir.iterdir():
            if not type_dir.is_dir():
                continue
            
            # Iterate through date directories
            for date_dir in type_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                # Check if directory is old
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    
                    if dir_date < cutoff_date:
                        # Delete all files in the directory
                        for log_file in date_dir.iterdir():
                            if log_file.is_file():
                                log_file.unlink()
                                deleted_count += 1
                        
                        # Remove empty directory
                        if not any(date_dir.iterdir()):
                            date_dir.rmdir()
                            
                except ValueError:
                    # Skip directories that don't match date format
                    continue
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old log files (older than {days} days)")
            
    except Exception as e:
        print(f"Error during log cleanup: {e}")


# Create logger instances for different purposes
app_logger = CustomLogger("app", "application")
security_logger = CustomLogger("security", "security")
db_logger = CustomLogger("database", "database")
agent_logger = CustomLogger("agent", "agent")
api_logger = CustomLogger("api", "api")


# Example usage function
def get_logger(name: str, log_type: str = "application") -> CustomLogger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        log_type: Type of log
        
    Returns:
        CustomLogger: Logger instance
    """
    return CustomLogger(name, log_type)
