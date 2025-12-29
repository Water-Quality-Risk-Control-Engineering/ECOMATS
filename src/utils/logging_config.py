"""
Unified Logging Configuration.
Centralized logging setup for ECOMATS.
"""

import logging
import sys

# Agent loggers to suppress
AGENT_LOGGERS = [
    'src.agents.Creative_Designing_agent',
    'src.agents.Assessment_Screening_agent_A',
    'src.agents.Assessment_Screening_agent_B',
    'src.agents.Assessment_Screening_agent_C',
    'src.agents.Assessment_Screening_agent_Overall',
    'src.agents.Mechanism_Mining_agent',
    'src.agents.Synthesis_Guiding_agent',
    'src.agents.Operation_Suggesting_agent',
    'src.agents.task_organizing_agent',
    'src.agents.Extracting_agent',
]

# Third-party loggers to suppress
THIRD_PARTY_LOGGERS = [
    'httpx',
    'openai',
    'chromadb',
    'urllib3',
]


def setup_logging(level: int = logging.WARNING, suppress_agents: bool = True):
    """
    Configure unified logging for ECOMATS.
    
    Args:
        level: Base logging level (default: WARNING)
        suppress_agents: Whether to suppress agent-specific logs (default: True)
    """
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    if suppress_agents:
        # Suppress agent logs to CRITICAL
        for logger_name in AGENT_LOGGERS:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    
    # Suppress third-party library logs
    for logger_name in THIRD_PARTY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
