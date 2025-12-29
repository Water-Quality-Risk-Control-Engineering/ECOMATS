"""
Task Callback Factory.
Creates callbacks for monitoring parallel task execution.
"""

import time


def create_task_callback_factory(monitor, task_start_times, current_agent_context, last_completed_agent):
    """
    Create task_callback factory function that supports parallel tasks.
    
    This factory handles:
    - Parallel task timing (evaluation agents A/B/C share start time)
    - Agent interaction tracking
    - Monitoring data collection
    
    Args:
        monitor: Workflow monitor instance
        task_start_times: Dict to store task start times
        current_agent_context: Thread-local storage for current agent
        last_completed_agent: List containing last completed agent role
    
    Returns:
        function: Factory function that creates task_callback
    """
    
    def create_task_callback(task_completion_times, crew_start_time, task_counter, suffix=""):
        eval_start_key = f'eval_start_time{suffix}'
        
        def task_callback(task_output):
            task_counter[0] += 1
            task_id = task_counter[0]
            
            agent_str = getattr(task_output, 'agent', None) or 'Unknown'
            task_name = getattr(task_output, 'name', None) or f"{agent_str}_Task_{task_id}"
            task_description = getattr(task_output, 'description', 'N/A')
            agent_name = agent_str
            agent_role = agent_str
            
            current_agent_context.role = agent_role
            
            json_output = None
            if hasattr(task_output, 'json_dict') and task_output.json_dict:
                json_output = task_output.json_dict
            
            if monitor:
                current_time = time.time()
                
                # Detect parallel tasks: A/B/C share same start time
                is_parallel_eval = 'Assessment_Screening_agent_' in agent_role and agent_role[-1] in 'ABC'
                
                if is_parallel_eval:
                    if eval_start_key not in task_start_times:
                        if task_completion_times:
                            task_start_times[eval_start_key] = task_completion_times[-1]
                        elif crew_start_time[0]:
                            task_start_times[eval_start_key] = crew_start_time[0]
                        else:
                            task_start_times[eval_start_key] = current_time
                    actual_start = task_start_times[eval_start_key]
                else:
                    if task_completion_times:
                        actual_start = task_completion_times[-1]
                    elif crew_start_time[0]:
                        actual_start = crew_start_time[0]
                    else:
                        actual_start = current_time
                
                task_completion_times.append(current_time)
                
                unique_task_key = f"{agent_role}_{task_id}"
                if unique_task_key not in task_start_times:
                    task_start_times[unique_task_key] = actual_start
                    monitor.start_agent_execution(agent_name, agent_role, task_name, task_description)
                    if monitor._current_execution:
                        monitor._current_execution.start_time = actual_start
                monitor.end_agent_execution(output=str(task_output), json_output=json_output, agent_role=agent_role)
                
                # Record agent interaction
                if last_completed_agent[0] and last_completed_agent[0] != agent_role:
                    monitor.record_interaction(
                        from_agent=last_completed_agent[0],
                        to_agent=agent_role,
                        interaction_type="task_handoff",
                        content=f"Task completed: {task_name}"
                    )
                last_completed_agent[0] = agent_role
        
        return task_callback
    
    return create_task_callback
