"""
ECOMATS Event Listener Module.

CrewAI 1.8.x 标准 EventListener 实现，替代手动 callback_factory。

功能:
1. 标准化事件监听 (task_start, task_end, tool_call)
2. 与 WorkflowMonitor 集成
3. 支持并行任务追踪
4. 实时进度输出

Usage:
    from workflow.event_listener import ECOMATSEventListener
    
    listener = ECOMATSEventListener(monitor=monitor)
    crew = Crew(..., callbacks=[listener])
"""

import time
import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ToolCallRecord:
    """工具调用记录"""
    agent_role: str
    tool_name: str
    inputs: Dict[str, Any]
    output: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    success: bool = True
    error: Optional[str] = None


class ECOMATSEventListener:
    """
    ECOMATS 事件监听器 - 基于 CrewAI 1.8.x 标准接口
    
    替代 callback_factory.py，提供更标准化的事件监听机制。
    
    Attributes:
        monitor: WorkflowMonitor 实例，用于记录执行数据
        verbose: 是否输出实时进度
        tool_calls: 工具调用记录列表
    """
    
    def __init__(
        self, 
        monitor=None, 
        verbose: bool = True,
        track_tools: bool = True
    ):
        """
        初始化事件监听器
        
        Args:
            monitor: WorkflowMonitor 实例（可选）
            verbose: 是否在终端显示实时进度
            track_tools: 是否追踪工具调用
        """
        self.monitor = monitor
        self.verbose = verbose
        self.track_tools = track_tools
        
        # 线程安全的状态追踪
        self._lock = threading.Lock()
        self._current_agent: Optional[str] = None
        self._task_start_times: Dict[str, float] = {}
        self._parallel_eval_start: Optional[float] = None
        self._last_completed_agent: Optional[str] = None
        
        # 工具调用追踪
        self.tool_calls: List[ToolCallRecord] = []
        self._tool_calls_by_agent: Dict[str, Dict[str, int]] = {}
    
    # ================================================================
    # CrewAI 标准事件回调接口
    # ================================================================
    
    def on_task_start(self, task) -> None:
        """
        任务开始事件
        
        Args:
            task: CrewAI Task 对象
        """
        with self._lock:
            agent = getattr(task, 'agent', None)
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
            task_name = getattr(task, 'name', None) or getattr(task, 'description', 'Task')[:50]
            task_description = getattr(task, 'description', '')
            
            self._current_agent = agent_role
            current_time = time.time()
            
            # 检测并行评估任务 (A/B/C)
            is_parallel_eval = self._is_parallel_eval_task(agent_role)
            
            if is_parallel_eval and self._parallel_eval_start is None:
                self._parallel_eval_start = current_time
            
            # 记录任务开始时间
            task_key = f"{agent_role}_{id(task)}"
            self._task_start_times[task_key] = current_time
            
            # 通知 WorkflowMonitor
            if self.monitor:
                self.monitor.start_agent_execution(
                    agent_name=agent_role,
                    agent_role=agent_role,
                    task_name=task_name,
                    task_description=task_description
                )
            
            if self.verbose:
                print(f"🚀 [{agent_role}] 任务开始: {task_name[:40]}...")
    
    def on_task_end(self, task, output) -> None:
        """
        任务完成事件
        
        Args:
            task: CrewAI Task 对象
            output: 任务输出
        """
        with self._lock:
            agent = getattr(task, 'agent', None)
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
            task_name = getattr(task, 'name', None) or 'Task'
            
            current_time = time.time()
            task_key = f"{agent_role}_{id(task)}"
            
            # 计算耗时
            start_time = self._task_start_times.pop(task_key, current_time)
            duration = current_time - start_time
            
            # 获取输出
            output_str = str(output) if output else ''
            json_output = None
            if hasattr(output, 'json_dict') and output.json_dict:
                json_output = output.json_dict
            
            # 通知 WorkflowMonitor
            if self.monitor:
                self.monitor.end_agent_execution(
                    output=output_str,
                    json_output=json_output,
                    agent_role=agent_role
                )
                
                # 记录 Agent 交互
                if self._last_completed_agent and self._last_completed_agent != agent_role:
                    self.monitor.record_interaction(
                        from_agent=self._last_completed_agent,
                        to_agent=agent_role,
                        interaction_type="task_handoff",
                        content=f"Task completed: {task_name}"
                    )
            
            self._last_completed_agent = agent_role
            
            if self.verbose:
                print(f"✅ [{agent_role}] 任务完成 ({duration:.2f}s)")
    
    def on_tool_start(self, tool_name: str, inputs: Dict[str, Any]) -> None:
        """
        工具调用开始事件
        
        Args:
            tool_name: 工具名称
            inputs: 工具输入参数
        """
        if not self.track_tools:
            return
        
        with self._lock:
            agent_role = self._current_agent or 'Unknown'
            
            # 记录工具调用
            record = ToolCallRecord(
                agent_role=agent_role,
                tool_name=tool_name,
                inputs=inputs,
                start_time=time.time()
            )
            self.tool_calls.append(record)
            
            # 按 Agent 分组计数
            if agent_role not in self._tool_calls_by_agent:
                self._tool_calls_by_agent[agent_role] = {}
            if tool_name not in self._tool_calls_by_agent[agent_role]:
                self._tool_calls_by_agent[agent_role][tool_name] = 0
            self._tool_calls_by_agent[agent_role][tool_name] += 1
            
            count = self._tool_calls_by_agent[agent_role][tool_name]
            
            if self.verbose:
                print(f"  🔧 [{agent_role[:15]}] {tool_name} (#{count})")
    
    def on_tool_end(self, tool_name: str, output: str) -> None:
        """
        工具调用完成事件
        
        Args:
            tool_name: 工具名称
            output: 工具输出
        """
        if not self.track_tools:
            return
        
        with self._lock:
            # 找到最近的匹配工具调用记录并更新
            for record in reversed(self.tool_calls):
                if record.tool_name == tool_name and record.output is None:
                    record.output = str(output)[:500] if output else ''
                    record.end_time = time.time()
                    break
    
    def on_tool_error(self, tool_name: str, error: str) -> None:
        """
        工具调用错误事件
        
        Args:
            tool_name: 工具名称
            error: 错误信息
        """
        if not self.track_tools:
            return
        
        with self._lock:
            # 找到最近的匹配工具调用记录并更新
            for record in reversed(self.tool_calls):
                if record.tool_name == tool_name and record.output is None:
                    record.error = str(error)
                    record.success = False
                    record.end_time = time.time()
                    break
            
            if self.verbose:
                print(f"  ❌ [{tool_name}] 工具调用失败: {error[:50]}...")
    
    def on_crew_start(self, crew) -> None:
        """
        Crew 开始执行事件
        
        Args:
            crew: CrewAI Crew 对象
        """
        if self.verbose:
            crew_name = getattr(crew, 'name', 'ECOMATS')
            agents_count = len(getattr(crew, 'agents', []))
            tasks_count = len(getattr(crew, 'tasks', []))
            print(f"\n🚀 Crew '{crew_name}' 开始执行")
            print(f"   Agents: {agents_count} | Tasks: {tasks_count}")
    
    def on_crew_end(self, crew, result) -> None:
        """
        Crew 执行完成事件
        
        Args:
            crew: CrewAI Crew 对象
            result: 执行结果
        """
        if self.verbose:
            crew_name = getattr(crew, 'name', 'ECOMATS')
            print(f"\n✅ Crew '{crew_name}' 执行完成")
            self._print_tool_summary()
    
    # ================================================================
    # 辅助方法
    # ================================================================
    
    def _is_parallel_eval_task(self, agent_role: str) -> bool:
        """检测是否为并行评估任务 (A/B/C)"""
        return 'Assessment_Screening_agent_' in agent_role and agent_role[-1] in 'ABC'
    
    def _print_tool_summary(self) -> None:
        """打印工具调用汇总"""
        if not self.tool_calls:
            return
        
        print("\n📊 工具调用汇总:")
        for agent_role, tools in self._tool_calls_by_agent.items():
            total = sum(tools.values())
            print(f"   [{agent_role}] 共调用 {total} 次工具")
            for tool_name, count in sorted(tools.items(), key=lambda x: -x[1]):
                print(f"      - {tool_name}: {count}次")
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """
        获取工具调用统计
        
        Returns:
            工具调用统计字典
        """
        total_calls = len(self.tool_calls)
        successful = sum(1 for r in self.tool_calls if r.success)
        failed = total_calls - successful
        
        avg_duration = 0.0
        if total_calls > 0:
            durations = [r.end_time - r.start_time for r in self.tool_calls if r.end_time > 0]
            avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return {
            "total_calls": total_calls,
            "successful": successful,
            "failed": failed,
            "avg_duration_seconds": round(avg_duration, 3),
            "by_agent": self._tool_calls_by_agent.copy()
        }
    
    # ================================================================
    # CrewAI step_callback 兼容接口
    # ================================================================
    
    def __call__(self, step_output) -> None:
        """
        兼容 CrewAI step_callback 接口
        
        可直接用作 Crew(step_callback=listener)
        
        Args:
            step_output: CrewAI 步骤输出
        """
        # 检测是否为工具调用
        if hasattr(step_output, 'tool'):
            tool_name = step_output.tool
            tool_input = getattr(step_output, 'tool_input', {})
            self.on_tool_start(tool_name, tool_input)
        
        # 尝试获取 Agent 信息
        if hasattr(step_output, 'agent'):
            agent = step_output.agent
            if hasattr(agent, 'role'):
                with self._lock:
                    self._current_agent = agent.role


def create_event_listener(
    monitor=None,
    verbose: bool = True,
    track_tools: bool = True
) -> ECOMATSEventListener:
    """
    创建事件监听器的工厂函数
    
    Args:
        monitor: WorkflowMonitor 实例
        verbose: 是否显示实时进度
        track_tools: 是否追踪工具调用
    
    Returns:
        ECOMATSEventListener 实例
    """
    return ECOMATSEventListener(
        monitor=monitor,
        verbose=verbose,
        track_tools=track_tools
    )
