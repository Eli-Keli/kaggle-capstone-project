"""
Logging configuration for the Accessible Services Navigator.

This module sets up structured logging with ADK logging plugins to capture
agent invocations, tool calls, and performance metrics.
"""

import os
import logging
import structlog
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from google.adk.logging import configure_logging, LogLevel
except ImportError:
    # Fallback for when ADK is not installed
    configure_logging = None
    class LogLevel:
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"


# Define log directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    log_file_name: Optional[str] = None
) -> None:
    """
    Set up logging for the agent system.
    
    This function configures:
    - ADK logging plugins for agent traces
    - Structured logging with structlog
    - File and console handlers
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Whether to write logs to file
        enable_console_logging: Whether to write logs to console
        log_file_name: Custom log file name (default: agent_traces_TIMESTAMP.log)
    """
    # Convert string log level to ADK LogLevel enum
    adk_log_level = _get_adk_log_level(log_level)
    
    # Configure ADK logging (if available)
    if configure_logging is not None:
        configure_logging(
            level=adk_log_level,
            enable_cloud_logging=False,  # Disable for local development
        )
    
    # Set up Python standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up structlog processors
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add JSON renderer for file logging, console renderer for terminal
    if enable_file_logging:
        # Create log file with timestamp
        if not log_file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_name = f"agent_traces_{timestamp}.log"
        
        log_file_path = LOG_DIR / log_file_name
        
        # Configure file handler with JSON output
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        file_formatter = logging.Formatter(
            '%(message)s'  # structlog will handle the formatting
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        print(f"📝 Logging to: {log_file_path}")
    
    # Configure structlog
    structlog.configure(
        processors=processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set log level for ADK and related libraries
    logging.getLogger("google.adk").setLevel(getattr(logging, log_level.upper()))
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce noise
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def _get_adk_log_level(level_str: str) -> LogLevel:
    """
    Convert string log level to ADK LogLevel enum.
    
    Args:
        level_str: Log level as string
        
    Returns:
        ADK LogLevel enum value
    """
    level_mapping = {
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "ERROR": LogLevel.ERROR,
        "CRITICAL": LogLevel.CRITICAL,
    }
    
    return level_mapping.get(level_str.upper(), LogLevel.INFO)


def log_agent_invocation(
    logger: structlog.BoundLogger,
    agent_name: str,
    input_data: dict,
    session_id: str
) -> None:
    """
    Log an agent invocation with structured data.
    
    Args:
        logger: Structlog logger instance
        agent_name: Name of the agent being invoked
        input_data: Input data passed to the agent
        session_id: Current session identifier
    """
    logger.info(
        "agent_invocation",
        agent=agent_name,
        session_id=session_id,
        input_keys=list(input_data.keys()),
        event_type="agent_start"
    )


def log_agent_completion(
    logger: structlog.BoundLogger,
    agent_name: str,
    output_data: dict,
    session_id: str,
    duration_ms: float
) -> None:
    """
    Log an agent completion with structured data.
    
    Args:
        logger: Structlog logger instance
        agent_name: Name of the agent that completed
        output_data: Output data from the agent
        session_id: Current session identifier
        duration_ms: Duration of agent execution in milliseconds
    """
    logger.info(
        "agent_completion",
        agent=agent_name,
        session_id=session_id,
        output_keys=list(output_data.keys()),
        duration_ms=duration_ms,
        event_type="agent_end"
    )


def log_tool_call(
    logger: structlog.BoundLogger,
    tool_name: str,
    parameters: dict,
    session_id: str
) -> None:
    """
    Log a tool call with parameters.
    
    Args:
        logger: Structlog logger instance
        tool_name: Name of the tool being called
        parameters: Parameters passed to the tool
        session_id: Current session identifier
    """
    logger.info(
        "tool_call",
        tool=tool_name,
        session_id=session_id,
        parameters=parameters,
        event_type="tool_invocation"
    )


def log_error(
    logger: structlog.BoundLogger,
    error: Exception,
    context: dict,
    session_id: str
) -> None:
    """
    Log an error with context.
    
    Args:
        logger: Structlog logger instance
        error: Exception that occurred
        context: Additional context about the error
        session_id: Current session identifier
    """
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        session_id=session_id,
        context=context,
        event_type="error"
    )
