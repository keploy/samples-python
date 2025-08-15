import logging
import sys
from pythonjsonlogger import jsonlogger
from flask import has_request_context, request
import time

class RequestFormatter(jsonlogger.JsonFormatter):
    """Custom formatter to include request details in logs"""
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if has_request_context():
            log_record['url'] = request.url
            log_record['method'] = request.method
            log_record['ip'] = request.remote_addr
        
        # Add timestamp in ISO format
        log_record['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        # Add log level and message
        log_record['level'] = record.levelname
        log_record['message'] = record.getMessage()
        
        # Add logger name
        log_record['logger'] = record.name


def setup_logging(config):
    """Configure application logging"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Create formatter
    formatter = RequestFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )
    
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Configure Flask's default logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.ERROR)
    
    return logger


def get_logger(name):
    """Get a logger instance with the given name"""
    return logging.getLogger(name)
