"""
ECOMATS Workflow Module
Modular components for workflow execution.

CrewAI 1.8.x Features:
- EventListener: 标准化事件监听
- Flow: 声明式工作流编排
- HITL: 人工审核节点
- A2A: 跨项目智能体协作
"""

from .patches import apply_crewai_patches
from .callback_factory import create_task_callback_factory
from .embeddings import create_dashscope_embedder

# CrewAI 1.8.x new modules
from .event_listener import ECOMATSEventListener, create_event_listener
from .hitl import HITLManager, HITLDecision, create_hitl_manager
from .a2a import A2AClient, ECOMATSAgentServer, AgentCard, BioCrewClient

__all__ = [
    # Legacy
    'apply_crewai_patches',
    'create_task_callback_factory',
    'create_dashscope_embedder',
    # CrewAI 1.8.x
    'ECOMATSEventListener',
    'create_event_listener',
    'HITLManager',
    'HITLDecision', 
    'create_hitl_manager',
    'A2AClient',
    'ECOMATSAgentServer',
    'AgentCard',
    'BioCrewClient',
]
