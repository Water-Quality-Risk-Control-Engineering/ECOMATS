#!/usr/bin/env python3
"""
Workflow Monitor Module.

Features:
1. Record overall process execution results
2. Track execution time of each Agent/Task
3. Save complete Agent interaction records
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class AgentExecution:
    """Agent execution record."""
    agent_name: str
    agent_role: str
    task_name: str
    task_description: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_seconds: float = 0.0
    status: str = "pending"  # pending, running, completed, error
    output: str = ""
    json_output: Optional[Dict] = None
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "task_name": self.task_name,
            "task_description": self.task_description,
            "start_time": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "",
            "end_time": datetime.fromtimestamp(self.end_time).strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "",
            "duration_seconds": round(self.duration_seconds, 2),
            "duration_formatted": self._format_duration(),
            "status": self.status,
            "output": self.output,
            "json_output": self.json_output,
            "error_message": self.error_message
        }
    
    def _format_duration(self) -> str:
        """Format duration."""
        if self.duration_seconds < 60:
            return f"{self.duration_seconds:.2f}s"
        elif self.duration_seconds < 3600:
            minutes = int(self.duration_seconds // 60)
            seconds = self.duration_seconds % 60
            return f"{minutes}m {seconds:.2f}s"
        else:
            hours = int(self.duration_seconds // 3600)
            minutes = int((self.duration_seconds % 3600) // 60)
            seconds = self.duration_seconds % 60
            return f"{hours}h {minutes}m {seconds:.2f}s"


@dataclass  
class InteractionRecord:
    """Agent interaction record."""
    timestamp: float
    from_agent: str
    to_agent: str
    interaction_type: str  # task_handoff, context_sharing, result_passing
    content: str
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "interaction_type": self.interaction_type,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content
        }


class WorkflowMonitor:
    """Workflow Monitor.
    
    Used to track and record the execution of the entire workflow, including:
    - Execution time of each Agent/Task
    - Interaction records between Agents
    - Overall workflow results and statistics
    """
    
    def __init__(self, workflow_id: str = None, output_dir: str = None):
        """Initialize monitor.
        
        Args:
            workflow_id: Unique workflow identifier, defaults to timestamp
            output_dir: Output directory, defaults to outputs folder in project root
        """
        self.workflow_id = workflow_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()
        self.end_time: float = 0.0
        
        # Set output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            # Automatically detect project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.output_dir = os.path.join(project_root, "outputs")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Workflow metadata
        self.user_requirement: str = ""
        self.workflow_mode: str = ""
        self.is_async: bool = False
        
        # Agent execution records
        self.agent_executions: List[AgentExecution] = []
        self._current_execution: Optional[AgentExecution] = None
        self._execution_map: Dict[str, AgentExecution] = {}  # Support parallel tasks
        
        # Interaction records
        self.interactions: List[InteractionRecord] = []
        
        # Final result
        self.final_result: Any = None
        self.workflow_status: str = "running"  # running, completed, error
        self.error_message: str = ""
        
        # Task counter
        self._task_counter = 0
    
    def set_workflow_info(self, user_requirement: str, workflow_mode: str, is_async: bool = False):
        """Set basic workflow information.
        
        Args:
            user_requirement: User requirement
            workflow_mode: Workflow mode (preset/autonomous)
            is_async: Whether to execute asynchronously
        """
        self.user_requirement = user_requirement
        self.workflow_mode = workflow_mode
        self.is_async = is_async
    
    def start_agent_execution(self, agent_name: str, agent_role: str, 
                              task_name: str, task_description: str) -> None:
        """Start recording Agent execution.
        
        Args:
            agent_name: Agent name
            agent_role: Agent role
            task_name: Task name
            task_description: Task description
        """
        self._task_counter += 1
        
        execution = AgentExecution(
            agent_name=agent_name,
            agent_role=agent_role,
            task_name=task_name or f"Task_{self._task_counter}",
            task_description=task_description,
            start_time=time.time(),
            status="running"
        )
        
        # Support parallel tasks: use agent_role as key
        self._execution_map[agent_role] = execution
        self._current_execution = execution
        self.agent_executions.append(execution)
        
        # Silent mode: do not output monitoring info to console, only record to report
        # print(f"📊 [Monitor] Agent开始执行: {agent_role} - {task_name}")
    
    def end_agent_execution(self, output: str = "", json_output: Dict = None, 
                           error: str = "", agent_role: str = None) -> None:
        """End specified or current Agent execution record.
        
        Args:
            output: Execution output
            json_output: JSON format output
            error: Error message
            agent_role: Specified Agent role (for parallel tasks)
        """
        # Prioritize using specified agent_role, otherwise use _current_execution
        if agent_role and agent_role in self._execution_map:
            execution = self._execution_map[agent_role]
        else:
            execution = self._current_execution
        
        if execution:
            execution.end_time = time.time()
            execution.duration_seconds = (
                execution.end_time - execution.start_time
            )
            execution.output = str(output)
            execution.json_output = json_output
            
            if error:
                execution.status = "error"
                execution.error_message = error
            else:
                execution.status = "completed"
            
            # Remove completed execution from map
            if agent_role and agent_role in self._execution_map:
                del self._execution_map[agent_role]
            
            # Silent mode
            # duration = execution._format_duration()
            # print(f"✅ [Monitor] Agent执行完成: {execution.agent_role} - 耗时: {duration}")
            
            if execution == self._current_execution:
                self._current_execution = None
    
    def record_interaction(self, from_agent: str, to_agent: str, 
                          interaction_type: str, content: str) -> None:
        """Record interaction between Agents.
        
        Args:
            from_agent: Source Agent
            to_agent: Target Agent  
            interaction_type: Interaction type (task_handoff/context_sharing/result_passing)
            content: Interaction content
        """
        interaction = InteractionRecord(
            timestamp=time.time(),
            from_agent=from_agent,
            to_agent=to_agent,
            interaction_type=interaction_type,
            content=content
        )
        self.interactions.append(interaction)
    
    def create_task_callback(self):
        """Create task callback function for CrewAI.
        
        Returns:
            Function usable for Crew task_callback parameter
        """
        def task_callback(task_output):
            """Callback function when task is completed."""
            # Get task information
            task_name = getattr(task_output, 'name', None) or f"Task_{self._task_counter + 1}"
            task_description = getattr(task_output, 'description', 'N/A')
            
            # Try to get Agent information
            agent = getattr(task_output, 'agent', None)
            agent_name = getattr(agent, 'name', 'Unknown') if agent else 'Unknown'
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
            
            # Get output
            output_str = str(task_output)
            json_output = None
            if hasattr(task_output, 'json_dict') and task_output.json_dict:
                json_output = task_output.json_dict
            
            # If no current execution record, create one (for handling cases without explicit start)
            if not self._current_execution:
                self.start_agent_execution(agent_name, agent_role, task_name, task_description)
            
            # End execution record
            self.end_agent_execution(output=output_str, json_output=json_output)
            
            # Record interaction (task completed -> next task)
            if len(self.agent_executions) > 1:
                prev_agent = self.agent_executions[-2].agent_role
                curr_agent = agent_role
                self.record_interaction(
                    from_agent=prev_agent,
                    to_agent=curr_agent,
                    interaction_type="task_handoff",
                    content=f"Task completed: {task_name}"
                )
        
        return task_callback
    
    def set_final_result(self, result: Any, status: str = "completed", 
                        error: str = "") -> None:
        """Set final result.
        
        Args:
            result: Final result
            status: Status (completed/error)
            error: Error message
        """
        self.end_time = time.time()
        self.final_result = result
        self.workflow_status = status
        self.error_message = error
    
    def get_summary(self) -> Dict:
        """Get workflow execution summary.
        
        Returns:
            Dictionary containing all monitoring data
        """
        total_duration = self.end_time - self.start_time if self.end_time else time.time() - self.start_time
        
        # Calculate total time for each Agent
        agent_durations = {}
        for execution in self.agent_executions:
            role = execution.agent_role
            if role not in agent_durations:
                agent_durations[role] = 0.0
            agent_durations[role] += execution.duration_seconds
        
        return {
            "workflow_info": {
                "workflow_id": self.workflow_id,
                "user_requirement": self.user_requirement,
                "workflow_mode": self.workflow_mode,
                "is_async": self.is_async,
                "start_time": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.fromtimestamp(self.end_time).strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "",
                "total_duration_seconds": round(total_duration, 2),
                "total_duration_formatted": self._format_duration(total_duration),
                "status": self.workflow_status,
                "error_message": self.error_message
            },
            "agent_statistics": {
                "total_agents": len(set(e.agent_role for e in self.agent_executions)),
                "total_tasks": len(self.agent_executions),
                "agent_durations": {k: round(v, 2) for k, v in agent_durations.items()},
                "slowest_agent": max(agent_durations.items(), key=lambda x: x[1])[0] if agent_durations else None,
                "fastest_agent": min(agent_durations.items(), key=lambda x: x[1])[0] if agent_durations else None
            },
            "agent_executions": [e.to_dict() for e in self.agent_executions],
            "interactions": [i.to_dict() for i in self.interactions],
            "final_result": str(self.final_result) if self.final_result else None
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration."""
        if seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.2f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs:.2f}s"
    
    def save_report(self, filename: str = None) -> str:
        """Save monitoring report.
        
        Args:
            filename: Filename, defaults to auto-generated
            
        Returns:
            Path to saved file
        """
        if not filename:
            mode_str = f"{self.workflow_mode}_{'async' if self.is_async else 'sync'}"
            filename = f"monitor_report_{self.workflow_id}_{mode_str}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        summary = self.get_summary()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # print(f"📊 [Monitor] 监控报告已保存: {filepath}")
        return filepath
    
    def save_readable_report(self, filename: str = None) -> str:
        """Save readable text format monitoring report.
        
        Args:
            filename: Filename, defaults to auto-generated
            
        Returns:
            Path to saved file
        """
        if not filename:
            mode_str = f"{self.workflow_mode}_{'async' if self.is_async else 'sync'}"
            filename = f"monitor_report_{self.workflow_id}_{mode_str}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        summary = self.get_summary()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ECOMATS 工作流监控报告 / Workflow Monitor Report\n")
            f.write("=" * 80 + "\n\n")
            
            # 1. Workflow basic information
            f.write("📋 工作流信息 / Workflow Info\n")
            f.write("-" * 40 + "\n")
            info = summary["workflow_info"]
            f.write(f"  工作流ID: {info['workflow_id']}\n")
            f.write(f"  用户需求: {info['user_requirement'][:100]}...\n" if len(info['user_requirement']) > 100 else f"  用户需求: {info['user_requirement']}\n")
            f.write(f"  工作模式: {info['workflow_mode']} ({'异步' if info['is_async'] else '同步'})\n")
            f.write(f"  开始时间: {info['start_time']}\n")
            f.write(f"  结束时间: {info['end_time']}\n")
            f.write(f"  总耗时: {info['total_duration_formatted']}\n")
            f.write(f"  状态: {info['status']}\n")
            if info['error_message']:
                f.write(f"  错误: {info['error_message']}\n")
            f.write("\n")
            
            # 2. Agent statistics
            f.write("📊 Agent统计 / Agent Statistics\n")
            f.write("-" * 40 + "\n")
            stats = summary["agent_statistics"]
            f.write(f"  总Agent数: {stats['total_agents']}\n")
            f.write(f"  总任务数: {stats['total_tasks']}\n")
            f.write(f"  最慢Agent: {stats['slowest_agent']}\n")
            f.write(f"  最快Agent: {stats['fastest_agent']}\n")
            f.write("\n")
            
            # 3. Detailed Agent durations
            f.write("⏱️ Agent耗时详情 / Agent Duration Details\n")
            f.write("-" * 40 + "\n")
            if stats['agent_durations'] and max(stats['agent_durations'].values()) > 0:
                max_duration = max(stats['agent_durations'].values())
                for role, duration in sorted(stats['agent_durations'].items(), key=lambda x: x[1], reverse=True):
                    bar_length = int(duration / max_duration * 30)
                    bar = "█" * bar_length + "░" * (30 - bar_length)
                    f.write(f"  {role[:30]:<30} | {bar} | {duration:.2f}s\n")
            else:
                f.write("  (无Agent耗时数据 / No agent duration data)\n")
            f.write("\n")
            
            # 4. Task execution timeline
            f.write("📜 任务执行时间线 / Task Execution Timeline\n")
            f.write("-" * 40 + "\n")
            for i, execution in enumerate(summary["agent_executions"], 1):
                status_icon = "✅" if execution["status"] == "completed" else "❌"
                f.write(f"  {i}. [{status_icon}] {execution['agent_role']}\n")
                f.write(f"     任务: {execution['task_name']}\n")
                f.write(f"     开始: {execution['start_time']} | 结束: {execution['end_time']}\n")
                f.write(f"     耗时: {execution['duration_formatted']}\n")
                if execution["error_message"]:
                    f.write(f"     错误: {execution['error_message']}\n")
                f.write("\n")
            
            # 5. Agent interaction records
            if summary["interactions"]:
                f.write("🔗 Agent交互记录 / Agent Interactions\n")
                f.write("-" * 40 + "\n")
                for i, interaction in enumerate(summary["interactions"], 1):
                    f.write(f"  {i}. [{interaction['timestamp']}]\n")
                    f.write(f"     {interaction['from_agent']} → {interaction['to_agent']}\n")
                    f.write(f"     类型: {interaction['interaction_type']}\n")
                    f.write(f"     内容: {interaction['content'][:100]}...\n" if len(interaction['content']) > 100 else f"     内容: {interaction['content']}\n")
                    f.write("\n")
            
            # 6. Final result summary
            f.write("📝 最终结果摘要 / Final Result Summary\n")
            f.write("-" * 40 + "\n")
            if summary["final_result"]:
                result_preview = summary["final_result"][:1000] + "..." if len(summary["final_result"]) > 1000 else summary["final_result"]
                f.write(f"{result_preview}\n")
            else:
                f.write("  (无结果)\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        
        # print(f"📊 [Monitor] 可读报告已保存: {filepath}")
        return filepath
    
    def print_summary(self) -> None:
        """Print execution summary in terminal."""
        summary = self.get_summary()
        
        print("\n" + "=" * 70)
        print("📊 工作流执行摘要 / Workflow Execution Summary")
        print("=" * 70)
        
        # Basic information
        info = summary["workflow_info"]
        print(f"\n⏱️ 总耗时: {info['total_duration_formatted']}")
        print(f"📌 状态: {info['status']}")
        
        # Agent statistics
        stats = summary["agent_statistics"]
        print(f"\n📋 执行了 {stats['total_tasks']} 个任务，涉及 {stats['total_agents']} 个Agent")
        
        # Duration ranking
        print("\n⏱️ Agent耗时排行:")
        for i, (role, duration) in enumerate(sorted(stats['agent_durations'].items(), 
                                                      key=lambda x: x[1], reverse=True), 1):
            print(f"   {i}. {role}: {duration:.2f}s")
        
        print("\n" + "=" * 70)


# Global monitor instance (optional usage)
_global_monitor: Optional[WorkflowMonitor] = None

def get_monitor() -> Optional[WorkflowMonitor]:
    """Get global monitor instance."""
    return _global_monitor

def create_monitor(workflow_id: str = None, output_dir: str = None) -> WorkflowMonitor:
    """Create and set global monitor."""
    global _global_monitor
    _global_monitor = WorkflowMonitor(workflow_id, output_dir)
    return _global_monitor
