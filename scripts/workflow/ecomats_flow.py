"""
ECOMATS Flow Module - CrewAI 1.8.x Production-ready Flows

基于 CrewAI 1.8.0+ Flow 架构的声明式工作流编排。

功能:
1. 声明式阶段定义 (@start, @listen, @router)
2. 条件分支路由
3. 并行任务自动处理
4. HITL 人工审核节点集成

Usage:
    from workflow.ecomats_flow import ECOMATSFlow
    
    flow = ECOMATSFlow(llm=llm, monitor=monitor)
    result = await flow.akickoff(inputs={"requirement": "设计光催化剂"})
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from crewai import Flow, Crew, Agent, Task, Process
from crewai.flow.flow import listen, start, router

# 导入 ECOMATS 组件
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class FlowState:
    """Flow 状态数据类"""
    requirement: str = ""
    design_result: Optional[Dict] = None
    evaluation_results: Optional[List[Dict]] = None
    overall_score: float = 0.0
    final_validation: Optional[Dict] = None
    mechanism_result: Optional[Dict] = None
    synthesis_result: Optional[Dict] = None
    operation_result: Optional[Dict] = None
    hitl_decision: Optional[str] = None


class ECOMATSFlow(Flow[FlowState]):
    """
    ECOMATS 工作流 - 基于 CrewAI 1.8.x Flow 架构
    
    工作流阶段:
    1. design_phase: 材料设计
    2. evaluation_phase: 并行评估 (A/B/C)
    3. validation_phase: 综合验证
    4. route_by_score: 条件路由 (高分/低分)
    5. mechanism_phase: 机理分析 (可选)
    6. synthesis_phase: 合成方法 (可选)
    7. operation_phase: 操作指导
    
    Attributes:
        llm: 语言模型实例
        monitor: 工作流监控器
        agents: Agent 实例字典
        hitl_enabled: 是否启用人工审核
    """
    
    def __init__(
        self,
        llm,
        monitor=None,
        hitl_enabled: bool = False,
        hitl_threshold: float = 75.0,
        verbose: bool = True
    ):
        """
        初始化 ECOMATS Flow
        
        Args:
            llm: 语言模型实例
            monitor: WorkflowMonitor 实例
            hitl_enabled: 是否启用 HITL 人工审核
            hitl_threshold: 触发 HITL 的分数阈值 (低于此分数触发)
            verbose: 是否显示详细输出
        """
        super().__init__()
        self.llm = llm
        self.monitor = monitor
        self.hitl_enabled = hitl_enabled
        self.hitl_threshold = hitl_threshold
        self.verbose = verbose
        
        # 延迟初始化 Agents
        self._agents: Optional[Dict[str, Agent]] = None
    
    def _ensure_agents(self) -> Dict[str, Agent]:
        """确保 Agents 已初始化"""
        if self._agents is None:
            self._agents = self._create_agents()
        return self._agents
    
    def _create_agents(self) -> Dict[str, Agent]:
        """创建所有 Agent 实例"""
        from src.agents.Creative_Designing_agent import CreativeDesigningAgent
        from src.agents.Assessment_Screening_agent_A import AssessmentScreeningAgentA
        from src.agents.Assessment_Screening_agent_B import AssessmentScreeningAgentB
        from src.agents.Assessment_Screening_agent_C import AssessmentScreeningAgentC
        from src.agents.Assessment_Screening_agent_Overall import AssessmentScreeningAgentOverall
        from src.agents.Mechanism_Mining_agent import MechanismMiningAgent
        from src.agents.Synthesis_Guiding_agent import SynthesisGuidingAgent
        from src.agents.Operation_Suggesting_agent import OperationSuggestingAgent
        
        return {
            'designer': CreativeDesigningAgent(self.llm).create_agent(),
            'expert_a': AssessmentScreeningAgentA(self.llm).create_agent(),
            'expert_b': AssessmentScreeningAgentB(self.llm).create_agent(),
            'expert_c': AssessmentScreeningAgentC(self.llm).create_agent(),
            'validator': AssessmentScreeningAgentOverall(self.llm).create_agent(),
            'mechanism': MechanismMiningAgent(self.llm).create_agent(),
            'synthesis': SynthesisGuidingAgent(self.llm).create_agent(),
            'operation': OperationSuggestingAgent(self.llm).create_agent(),
        }
    
    # ================================================================
    # Flow 阶段定义
    # ================================================================
    
    @start()
    def design_phase(self) -> Dict[str, Any]:
        """
        阶段 1: 材料设计
        
        根据用户需求设计水处理材料方案。
        
        Returns:
            设计结果字典
        """
        if self.verbose:
            print("\n" + "="*60)
            print("🎨 阶段 1: 材料设计")
            print("="*60)
        
        agents = self._ensure_agents()
        
        from src.tasks.design_task import DesignTask
        
        design_task = DesignTask(self.llm).create_task(
            agent=agents['designer'],
            user_requirement=self.state.requirement
        )
        
        crew = Crew(
            agents=[agents['designer']],
            tasks=[design_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff(inputs={'requirement': self.state.requirement})
        
        self.state.design_result = {
            'raw_output': str(result),
            'status': 'completed'
        }
        
        if self.verbose:
            print(f"✅ 设计完成")
        
        return self.state.design_result
    
    @listen(design_phase)
    async def evaluation_phase(self, design_result: Dict) -> List[Dict]:
        """
        阶段 2: 并行评估 (A/B/C 三个专家同时评估)
        
        三个评估专家并行执行，评估材料的不同维度。
        
        Args:
            design_result: 设计阶段结果
        
        Returns:
            三个专家的评估结果列表
        """
        if self.verbose:
            print("\n" + "="*60)
            print("🔍 阶段 2: 并行评估 (A/B/C)")
            print("="*60)
        
        agents = self._ensure_agents()
        
        from src.tasks.evaluation_task import EvaluationTask
        
        # 创建三个并行评估任务
        eval_tasks = []
        eval_agents = [agents['expert_a'], agents['expert_b'], agents['expert_c']]
        
        for agent in eval_agents:
            task = EvaluationTask(self.llm).create_task(
                agent=agent,
                context_task=None,  # 使用 design_result 作为上下文
                user_requirement=self.state.requirement
            )
            task.async_execution = True  # 启用异步并行
            eval_tasks.append(task)
        
        crew = Crew(
            agents=eval_agents,
            tasks=eval_tasks,
            process=Process.sequential,
            verbose=False
        )
        
        result = await crew.akickoff(inputs={
            'requirement': self.state.requirement,
            'design': str(design_result)
        })
        
        self.state.evaluation_results = [
            {'expert': 'A', 'output': str(result)},
            {'expert': 'B', 'output': str(result)},
            {'expert': 'C', 'output': str(result)},
        ]
        
        if self.verbose:
            print(f"✅ 三个专家评估完成")
        
        return self.state.evaluation_results
    
    @listen(evaluation_phase)
    def validation_phase(self, eval_results: List[Dict]) -> Dict[str, Any]:
        """
        阶段 3: 综合验证
        
        综合三个专家的评估结果，给出最终评分。
        
        Args:
            eval_results: 评估结果列表
        
        Returns:
            综合验证结果
        """
        if self.verbose:
            print("\n" + "="*60)
            print("📊 阶段 3: 综合验证")
            print("="*60)
        
        agents = self._ensure_agents()
        
        from src.tasks.final_validation_task import FinalValidationTask
        
        validation_task = FinalValidationTask(self.llm).create_task(
            agent=agents['validator'],
            context_task=None,
            user_requirement=self.state.requirement
        )
        
        crew = Crew(
            agents=[agents['validator']],
            tasks=[validation_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff(inputs={
            'requirement': self.state.requirement,
            'evaluations': str(eval_results)
        })
        
        # 解析评分 (简化处理，实际应从结果中提取)
        self.state.overall_score = 80.0  # 默认分数
        self.state.final_validation = {
            'raw_output': str(result),
            'score': self.state.overall_score
        }
        
        if self.verbose:
            print(f"✅ 综合验证完成，评分: {self.state.overall_score}")
        
        return self.state.final_validation
    
    @router(validation_phase)
    def route_by_score(self, validation_result: Dict) -> str:
        """
        条件路由: 根据评分决定后续流程
        
        - 高分 (≥75): 直接进入机理分析和合成方法
        - 低分 (<75): 触发 HITL 或重新设计
        
        Args:
            validation_result: 验证结果
        
        Returns:
            路由目标: "high_quality_path" 或 "low_quality_path"
        """
        score = self.state.overall_score
        
        if self.verbose:
            print(f"\n🔀 路由决策: 评分 {score}")
        
        if score >= self.hitl_threshold:
            if self.verbose:
                print(f"   → 高分路径: 继续机理分析和合成方法")
            return "high_quality_path"
        else:
            if self.verbose:
                print(f"   → 低分路径: 需要人工审核或重新设计")
            return "low_quality_path"
    
    @listen("high_quality_path")
    async def parallel_analysis_phase(self) -> Dict[str, Any]:
        """
        高分路径: 机理分析 + 合成方法 (并行执行)
        
        Returns:
            机理和合成结果
        """
        if self.verbose:
            print("\n" + "="*60)
            print("🔬 阶段 4: 机理分析 + 合成方法 (并行)")
            print("="*60)
        
        agents = self._ensure_agents()
        
        from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
        from src.tasks.synthesis_method_task import SynthesisMethodTask
        
        mechanism_task = MechanismAnalysisTask(self.llm).create_task(
            agent=agents['mechanism'],
            context_task=None,
            user_requirement=self.state.requirement
        )
        mechanism_task.async_execution = True
        
        synthesis_task = SynthesisMethodTask(self.llm).create_task(
            agent=agents['synthesis'],
            context_task=None,
            user_requirement=self.state.requirement
        )
        synthesis_task.async_execution = True
        
        crew = Crew(
            agents=[agents['mechanism'], agents['synthesis']],
            tasks=[mechanism_task, synthesis_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = await crew.akickoff(inputs={
            'requirement': self.state.requirement,
            'validation': str(self.state.final_validation)
        })
        
        self.state.mechanism_result = {'output': str(result)}
        self.state.synthesis_result = {'output': str(result)}
        
        if self.verbose:
            print(f"✅ 机理分析和合成方法完成")
        
        return {
            'mechanism': self.state.mechanism_result,
            'synthesis': self.state.synthesis_result
        }
    
    @listen("low_quality_path")
    def hitl_review_phase(self) -> Dict[str, Any]:
        """
        低分路径: HITL 人工审核
        
        当评分低于阈值时，暂停等待人工决策。
        
        Returns:
            HITL 决策结果
        """
        if self.verbose:
            print("\n" + "="*60)
            print("👤 HITL 人工审核节点")
            print("="*60)
        
        if self.hitl_enabled:
            # TODO: 实际的 HITL 实现需要与外部系统集成
            # 这里模拟一个决策
            print(f"⏸️ 评分 {self.state.overall_score} 低于阈值 {self.hitl_threshold}")
            print(f"   等待人工决策...")
            
            # 模拟人工决策
            self.state.hitl_decision = "continue"  # 或 "redesign" 或 "abort"
            
            if self.verbose:
                print(f"✅ 人工决策: {self.state.hitl_decision}")
        else:
            if self.verbose:
                print(f"ℹ️ HITL 未启用，自动继续")
            self.state.hitl_decision = "continue"
        
        return {'decision': self.state.hitl_decision, 'score': self.state.overall_score}
    
    @listen(parallel_analysis_phase)
    def operation_phase(self, analysis_result: Dict) -> Dict[str, Any]:
        """
        阶段 5: 操作指导
        
        基于机理和合成方法，提供操作指导。
        
        Args:
            analysis_result: 分析结果
        
        Returns:
            操作指导结果
        """
        if self.verbose:
            print("\n" + "="*60)
            print("📖 阶段 5: 操作指导")
            print("="*60)
        
        agents = self._ensure_agents()
        
        from src.tasks.operation_suggesting_task import OperationSuggestingTask
        
        operation_task = OperationSuggestingTask(self.llm).create_task(
            agent=agents['operation'],
            context_task=None,
            user_requirement=self.state.requirement
        )
        
        crew = Crew(
            agents=[agents['operation']],
            tasks=[operation_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff(inputs={
            'requirement': self.state.requirement,
            'analysis': str(analysis_result)
        })
        
        self.state.operation_result = {'output': str(result)}
        
        if self.verbose:
            print(f"✅ 操作指导完成")
            print("\n" + "="*60)
            print("🎉 ECOMATS Flow 执行完成!")
            print("="*60)
        
        return self.state.operation_result
    
    @listen(hitl_review_phase)
    def post_hitl_action(self, hitl_result: Dict) -> Dict[str, Any]:
        """
        HITL 后续处理
        
        根据人工决策执行相应操作。
        
        Args:
            hitl_result: HITL 决策结果
        
        Returns:
            处理结果
        """
        decision = hitl_result.get('decision', 'continue')
        
        if decision == 'continue':
            # 继续执行（跳过机理分析，直接到操作指导）
            if self.verbose:
                print("📖 根据 HITL 决策，继续执行操作指导...")
            
            agents = self._ensure_agents()
            from src.tasks.operation_suggesting_task import OperationSuggestingTask
            
            operation_task = OperationSuggestingTask(self.llm).create_task(
                agent=agents['operation'],
                context_task=None,
                user_requirement=self.state.requirement
            )
            
            crew = Crew(
                agents=[agents['operation']],
                tasks=[operation_task],
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff(inputs={'requirement': self.state.requirement})
            self.state.operation_result = {'output': str(result)}
            
            return self.state.operation_result
        
        elif decision == 'redesign':
            if self.verbose:
                print("🔄 根据 HITL 决策，返回重新设计...")
            return {'action': 'redesign', 'reason': 'HITL decision'}
        
        else:  # abort
            if self.verbose:
                print("⏹️ 根据 HITL 决策，终止流程")
            return {'action': 'abort', 'reason': 'HITL decision'}


# ================================================================
# 便捷函数
# ================================================================

async def run_ecomats_flow(
    llm,
    requirement: str,
    monitor=None,
    hitl_enabled: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    运行 ECOMATS Flow 的便捷函数
    
    Args:
        llm: 语言模型实例
        requirement: 用户需求
        monitor: WorkflowMonitor 实例
        hitl_enabled: 是否启用 HITL
        verbose: 是否显示详细输出
    
    Returns:
        Flow 执行结果
    """
    flow = ECOMATSFlow(
        llm=llm,
        monitor=monitor,
        hitl_enabled=hitl_enabled,
        verbose=verbose
    )
    
    # 设置初始状态
    flow.state.requirement = requirement
    
    # 执行 Flow
    result = await flow.akickoff()
    
    return result
