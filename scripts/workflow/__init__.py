"""
ECOMATS Workflow Module
Modular components for workflow execution.
"""

from .patches import apply_crewai_patches
from .callback_factory import create_task_callback_factory
from .embeddings import create_dashscope_embedder

__all__ = [
    'apply_crewai_patches',
    'create_task_callback_factory',
    'create_dashscope_embedder',
]
