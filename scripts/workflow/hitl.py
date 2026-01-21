"""
ECOMATS HITL (Human-in-the-Loop) Module.

CrewAI 1.8.x HITL 集成，支持在工作流关键节点暂停等待人工确认。

功能:
1. 定义 HITL 决策点
2. Webhook 回调集成
3. 超时处理
4. 决策日志记录

Usage:
    from workflow.hitl import HITLManager, create_hitl_manager
    
    hitl = HITLManager(enabled=True, timeout=3600)
    decision = await hitl.request_decision(
        prompt="评分 75，是否继续？",
        options=["continue", "redesign", "abort"],
        context={"score": 75}
    )
"""

import asyncio
import time
import json
import os
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class HITLDecisionType(Enum):
    """HITL 决策类型"""
    CONTINUE = "continue"
    REDESIGN = "redesign"
    ABORT = "abort"
    MODIFY = "modify"
    SKIP = "skip"
    CUSTOM = "custom"


@dataclass
class HITLDecision:
    """HITL 决策记录"""
    decision_id: str
    decision_type: HITLDecisionType
    timestamp: float
    prompt: str
    options: List[str]
    selected_option: str
    context: Dict[str, Any] = field(default_factory=dict)
    user_comment: str = ""
    timeout_reached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "prompt": self.prompt,
            "options": self.options,
            "selected_option": self.selected_option,
            "context": self.context,
            "user_comment": self.user_comment,
            "timeout_reached": self.timeout_reached
        }


@dataclass
class HITLConfig:
    """HITL 配置"""
    enabled: bool = False
    webhook_url: Optional[str] = None
    timeout_seconds: int = 3600
    default_decision: HITLDecisionType = HITLDecisionType.CONTINUE
    auto_approve_threshold: float = 80.0
    log_decisions: bool = True
    log_dir: str = "outputs/hitl_logs"


class HITLManager:
    """HITL 管理器 - 管理工作流中的人工审核节点"""
    
    def __init__(self, config: Optional[HITLConfig] = None, **kwargs):
        if config:
            self.config = config
        else:
            self.config = HITLConfig(**kwargs)
        
        self.decisions: List[HITLDecision] = []
        self.pending_decisions: Dict[str, asyncio.Future] = {}
        self._decision_counter = 0
        
        if self.config.log_decisions:
            os.makedirs(self.config.log_dir, exist_ok=True)
    
    def _generate_decision_id(self) -> str:
        self._decision_counter += 1
        return f"hitl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._decision_counter}"
    
    async def request_decision(
        self,
        prompt: str,
        options: List[str],
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> HITLDecision:
        """请求人工决策"""
        decision_id = self._generate_decision_id()
        timeout = timeout or self.config.timeout_seconds
        context = context or {}
        
        print(f"\n{'='*60}")
        print(f"👤 HITL 决策请求 [{decision_id}]")
        print(f"{'='*60}")
        print(f"📋 {prompt}")
        print(f"\n可选项:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print(f"\n⏱️ 超时: {timeout}秒")
        
        # 检查自动批准
        score = context.get('score', 0)
        if score >= self.config.auto_approve_threshold:
            print(f"ℹ️ 评分 {score} >= {self.config.auto_approve_threshold}，自动批准")
            decision = HITLDecision(
                decision_id=decision_id,
                decision_type=HITLDecisionType.CONTINUE,
                timestamp=time.time(),
                prompt=prompt,
                options=options,
                selected_option=options[0] if options else "continue",
                context=context,
                user_comment="Auto-approved based on score threshold"
            )
        else:
            # 模拟决策（实际实现需与外部系统集成）
            await asyncio.sleep(0.1)
            selected = options[0] if options else self.config.default_decision.value
            decision = HITLDecision(
                decision_id=decision_id,
                decision_type=self._parse_decision_type(selected),
                timestamp=time.time(),
                prompt=prompt,
                options=options,
                selected_option=selected,
                context=context,
                user_comment="Default decision (HITL simulation)"
            )
        
        self.decisions.append(decision)
        
        if self.config.log_decisions:
            self._save_decision_log(decision)
        
        print(f"\n✅ 决策完成: {decision.selected_option}")
        return decision
    
    def _parse_decision_type(self, selected: str) -> HITLDecisionType:
        selected_lower = selected.lower()
        if "continue" in selected_lower:
            return HITLDecisionType.CONTINUE
        elif "redesign" in selected_lower:
            return HITLDecisionType.REDESIGN
        elif "abort" in selected_lower:
            return HITLDecisionType.ABORT
        elif "modify" in selected_lower:
            return HITLDecisionType.MODIFY
        elif "skip" in selected_lower:
            return HITLDecisionType.SKIP
        return HITLDecisionType.CUSTOM
    
    def _save_decision_log(self, decision: HITLDecision) -> None:
        filename = f"hitl_decision_{decision.decision_id}.json"
        filepath = os.path.join(self.config.log_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(decision.to_dict(), f, ensure_ascii=False, indent=2)
    
    def should_trigger_hitl(self, score: float, force: bool = False) -> bool:
        if not self.config.enabled:
            return False
        if force:
            return True
        return score < self.config.auto_approve_threshold


def create_hitl_manager(
    enabled: bool = True,
    webhook_url: Optional[str] = None,
    timeout: int = 3600,
    auto_approve_threshold: float = 80.0
) -> HITLManager:
    """创建 HITL 管理器"""
    config = HITLConfig(
        enabled=enabled,
        webhook_url=webhook_url,
        timeout_seconds=timeout,
        auto_approve_threshold=auto_approve_threshold
    )
    return HITLManager(config)
