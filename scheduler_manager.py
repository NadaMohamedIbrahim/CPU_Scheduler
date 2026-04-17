"""
scheduler_manager.py - Backend controller that unifies all schedulers
Handles both batch and live execution, dynamic process addition
"""

import time
import threading
from enum import Enum
from typing import List, Dict, Any, Callable, Optional
from process import Process
from fcfs import run_fcfs
from priority_scheduling import run as priority_run
from round_robin import run as rr_run
from sjf import sjf_non_preemptive, sjf_preemptive


class SchedulerType(Enum):
    """Supported scheduler types"""
    FCFS = "fcfs"
    SJF_NON_PREEMPTIVE = "sjf_non_preemptive"
    SJF_PREEMPTIVE = "sjf_preemptive"
    PRIORITY_NON_PREEMPTIVE = "priority_non_preemptive"
    PRIORITY_PREEMPTIVE = "priority_preemptive"
    ROUND_ROBIN = "round_robin"


class SchedulerManager:
    """Main controller for all scheduling operations"""
    
    def __init__(self):
        self.processes: List[Process] = []
        self.scheduler_type: Optional[SchedulerType] = None
        self.time_quantum: int = 2  # Default for Round Robin
        self.is_running = False
        self.is_paused = False
        self.current_time = 0
        self.gantt_chart: List[tuple] = []
        self.execution_thread: Optional[threading.Thread] = None
        
        # Callbacks for GUI updates
        self.callbacks: Dict[str, List[Callable]] = {
            "on_tick": [],           # Called every second in live mode
            "on_process_complete": [],  # Called when a process finishes
            "on_gantt_update": [],   # Called when Gantt chart updates
            "on_metrics_update": [], # Called when metrics change
            "on_complete": []        # Called when scheduling finishes
        }
    
    # ============ Callback Registration ============
    def register_callback(self, event: str, callback: Callable):
        """Register a callback function for GUI updates"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _notify(self, event: str, data: Any = None):
        """Notify all registered callbacks of an event"""
        for callback in self.callbacks.get(event, []):
            callback(data)
    
    # ============ Process Management ============
    def set_scheduler(self, scheduler_type: SchedulerType, time_quantum: int = None):
        """Set which scheduling algorithm to use"""
        self.scheduler_type = scheduler_type
        if time_quantum:
            self.time_quantum = time_quantum
    
    def add_process(self, pid: int, arrival_time: int, burst_time: int, priority: int = None):
        """Add a new process dynamically (can be called while running)"""
        new_process = Process(pid, arrival_time, burst_time, priority)
        self.processes.append(new_process)
        self.processes.sort(key=lambda x: x.arrival_time)
        self._notify("on_process_added", new_process)
        return new_process
    
    def add_processes_batch(self, processes_data: List[Dict]):
        """Add multiple processes at once from GUI input"""
        for p_data in processes_data:
            self.add_process(
                pid=p_data["pid"],
                arrival_time=p_data["arrival_time"],
                burst_time=p_data["burst_time"],
                priority=p_data.get("priority")
            )
    
    def reset(self):
        """Reset all processes and state for a new run"""
        for p in self.processes:
            p.reset()
        self.current_time = 0
        self.gantt_chart = []
        self.is_running = False
        self.is_paused = False
    
    # ============ Batch Execution (No Delay) ============
    def execute_batch(self) -> Dict[str, Any]:
        """Execute scheduling in batch mode - runs instantly"""
        self.reset()
        
        if not self.processes:
            return {"error": "No processes to schedule"}
        
        # Make a copy for execution
        import copy
        processes_copy = copy.deepcopy(self.processes)
        
        # Run the selected scheduler
        if self.scheduler_type == SchedulerType.FCFS:
            updated_processes, gantt = run_fcfs(processes_copy)
            
        elif self.scheduler_type == SchedulerType.ROUND_ROBIN:
            gantt, avg_wt, avg_tat = rr_run(processes_copy, self.time_quantum)
            updated_processes = processes_copy
            
        elif self.scheduler_type == SchedulerType.SJF_NON_PREEMPTIVE:
            updated_processes, gantt = sjf_non_preemptive(processes_copy)
            
        elif self.scheduler_type == SchedulerType.SJF_PREEMPTIVE:
            updated_processes, gantt = sjf_preemptive(processes_copy)
            
        elif self.scheduler_type == SchedulerType.PRIORITY_NON_PREEMPTIVE:
            updated_processes, gantt = priority_run(processes_copy, mode="non_preemptive")
            
        elif self.scheduler_type == SchedulerType.PRIORITY_PREEMPTIVE:
            updated_processes, gantt = priority_run(processes_copy, mode="preemptive")
            
        else:
            raise ValueError(f"Unknown scheduler type: {self.scheduler_type}")
        
        # Update original processes with results
        for i, p in enumerate(self.processes):
            p.completion_time = updated_processes[i].completion_time
            p.turnaround_time = updated_processes[i].turnaround_time
            p.waiting_time = updated_processes[i].waiting_time
            p.remaining_time = updated_processes[i].remaining_time
        
        self.gantt_chart = gantt
        
        return self.get_results()
    
    # ============ Live Execution (1 sec = 1 time unit) ============
    def execute_live(self):
        """Execute scheduling in live mode - 1 second per time unit"""
        self.reset()
        self.is_running = True
        
        def run_live():
            if self.scheduler_type == SchedulerType.FCFS:
                self._run_fcfs_live()
            elif self.scheduler_type == SchedulerType.ROUND_ROBIN:
                self._run_round_robin_live()
            elif self.scheduler_type == SchedulerType.SJF_PREEMPTIVE:
                self._run_sjf_preemptive_live()
            elif self.scheduler_type == SchedulerType.PRIORITY_PREEMPTIVE:
                self._run_priority_preemptive_live()
            elif self.scheduler_type == SchedulerType.SJF_NON_PREEMPTIVE:
                self._run_sjf_non_preemptive_live()
            elif self.scheduler_type == SchedulerType.PRIORITY_NON_PREEMPTIVE:
                self._run_priority_non_preemptive_live()
            
            self.is_running = False
            self._notify("on_complete", self.get_results())
        
        self.execution_thread = threading.Thread(target=run_live, daemon=True)
        self.execution_thread.start()
    
    def _run_fcfs_live(self):
            """FCFS with 1-second ticks (Dynamically Patched)"""
            is_completed = {p.pid: False for p in self.processes}
            completed = 0
            
            while completed < len(self.processes) and self.is_running:
                # Update tracker if new processes arrived
                for p in self.processes:
                    if p.pid not in is_completed:
                        is_completed[p.pid] = False
                        
                # Find the earliest arrived process that isn't completed
                next_p = None
                for p in self.processes:
                    if not is_completed[p.pid]:
                        if next_p is None or p.arrival_time < next_p.arrival_time or (p.arrival_time == next_p.arrival_time and p.pid < next_p.pid):
                            next_p = p
                            
                if next_p:
                    # Idle time waiting for arrival
                    while self.current_time < next_p.arrival_time and self.is_running:
                        while self.is_paused:
                            time.sleep(0.1)
                        time.sleep(1)
                        self.current_time += 1
                        self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                    
                    # Execute for burst time
                    for _ in range(next_p.burst_time):
                        while self.is_paused and self.is_running:
                            time.sleep(0.1)
                        if not self.is_running: return
                        
                        next_p.remaining_time -= 1
                        self.current_time += 1
                        
                        if self.gantt_chart and self.gantt_chart[-1][0] == next_p.pid:
                            pid, s, e = self.gantt_chart[-1]
                            self.gantt_chart[-1] = (pid, s, self.current_time)
                        else:
                            self.gantt_chart.append((next_p.pid, self.current_time - 1, self.current_time))
                        
                        self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                        time.sleep(1)
                    
                    next_p.completion_time = self.current_time
                    next_p.turnaround_time = next_p.completion_time - next_p.arrival_time
                    next_p.waiting_time = next_p.turnaround_time - next_p.burst_time
                    is_completed[next_p.pid] = True
                    completed += 1
                    self._notify("on_process_complete", next_p)

    def _run_round_robin_live(self):
            """Round Robin with 1-second ticks (Dynamically Patched)"""
            from collections import deque
            queue = deque()
            enqueued_pids = set()
            completed = 0
            
            while completed < len(self.processes) and self.is_running:
                # Check for newly arrived processes and add to queue
                sorted_procs = sorted(self.processes, key=lambda x: (x.arrival_time, x.pid))
                for p in sorted_procs:
                    if p.arrival_time <= self.current_time and p.pid not in enqueued_pids and p.remaining_time > 0:
                        queue.append(p)
                        enqueued_pids.add(p.pid)
                
                if not queue:
                    # Idle: fast forward 1 sec
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                    time.sleep(1)
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                    continue
                
                current = queue.popleft()
                exec_time = min(self.time_quantum, current.remaining_time)
                
                for _ in range(exec_time):
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                    if not self.is_running: return
                    
                    current.remaining_time -= 1
                    self.current_time += 1
                    
                    if self.gantt_chart and self.gantt_chart[-1][0] == current.pid:
                        pid, s, e = self.gantt_chart[-1]
                        self.gantt_chart[-1] = (pid, s, self.current_time)
                    else:
                        self.gantt_chart.append((current.pid, self.current_time - 1, self.current_time))
                    
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                    time.sleep(1)
                    
                    # Check for arrivals DURING execution to add BEFORE re-queuing the current process
                    sorted_procs = sorted(self.processes, key=lambda x: (x.arrival_time, x.pid))
                    for p in sorted_procs:
                        if p.arrival_time <= self.current_time and p.pid not in enqueued_pids and p.remaining_time > 0:
                            queue.append(p)
                            enqueued_pids.add(p.pid)
                
                if current.remaining_time > 0:
                    queue.append(current)
                else:
                    current.completion_time = self.current_time
                    current.turnaround_time = current.completion_time - current.arrival_time
                    current.waiting_time = current.turnaround_time - current.burst_time
                    completed += 1
                    self._notify("on_process_complete", current)

    def _run_sjf_preemptive_live(self):
            """SJF Preemptive (SRTF) with 1-second ticks (Dynamically Patched)"""
            is_completed = {p.pid: False for p in self.processes}
            completed = 0
            current_pid = None
            start_time = 0
            
            while completed < len(self.processes) and self.is_running:
                for p in self.processes:
                    if p.pid not in is_completed:
                        is_completed[p.pid] = False

                min_rem = float('inf')
                process_to_run = None
                
                for p in self.processes:
                    if p.arrival_time <= self.current_time and not is_completed[p.pid]:
                        if p.remaining_time < min_rem:
                            min_rem = p.remaining_time
                            process_to_run = p
                
                if process_to_run is not None:
                    p = process_to_run
                    if current_pid != p.pid:
                        if current_pid is not None and self.current_time > start_time:
                            self.gantt_chart.append((current_pid, start_time, self.current_time))
                        current_pid = p.pid
                        start_time = self.current_time
                    
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                    
                    p.remaining_time -= 1
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                    time.sleep(1)
                    
                    if p.remaining_time == 0:
                        is_completed[p.pid] = True
                        completed += 1
                        p.completion_time = self.current_time
                        p.turnaround_time = p.completion_time - p.arrival_time
                        p.waiting_time = p.turnaround_time - p.burst_time
                        self.gantt_chart.append((current_pid, start_time, self.current_time))
                        current_pid = None
                        self._notify("on_process_complete", p)
                else:
                    if current_pid is not None and self.current_time > start_time:
                        self.gantt_chart.append((current_pid, start_time, self.current_time))
                        current_pid = None
                    time.sleep(1)
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})

    def _run_priority_preemptive_live(self):
            """Priority Preemptive with 1-second ticks (Dynamically Patched)"""
            is_completed = {p.pid: False for p in self.processes}
            completed = 0
            current_pid = None
            start_time = 0
            
            while completed < len(self.processes) and self.is_running:
                for p in self.processes:
                    if p.pid not in is_completed:
                        is_completed[p.pid] = False

                highest_priority = float('inf')
                process_to_run = None
                
                for p in self.processes:
                    if p.arrival_time <= self.current_time and not is_completed[p.pid] and p.remaining_time > 0:
                        if p.priority < highest_priority:
                            highest_priority = p.priority
                            process_to_run = p
                
                if process_to_run is not None:
                    p = process_to_run
                    if current_pid != p.pid:
                        if current_pid is not None and self.current_time > start_time:
                            self.gantt_chart.append((current_pid, start_time, self.current_time))
                        current_pid = p.pid
                        start_time = self.current_time
                    
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                    
                    p.remaining_time -= 1
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                    time.sleep(1)
                    
                    if p.remaining_time == 0:
                        is_completed[p.pid] = True
                        completed += 1
                        p.completion_time = self.current_time
                        p.turnaround_time = p.completion_time - p.arrival_time
                        p.waiting_time = p.turnaround_time - p.burst_time
                        self.gantt_chart.append((current_pid, start_time, self.current_time))
                        current_pid = None
                        self._notify("on_process_complete", p)
                else:
                    if current_pid is not None and self.current_time > start_time:
                        self.gantt_chart.append((current_pid, start_time, self.current_time))
                        current_pid = None
                    time.sleep(1)
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})

    def _run_sjf_non_preemptive_live(self):
            """SJF Non-Preemptive with 1-second ticks (Dynamically Patched)"""
            is_completed = {p.pid: False for p in self.processes}
            completed = 0
            
            while completed < len(self.processes) and self.is_running:
                for p in self.processes:
                    if p.pid not in is_completed:
                        is_completed[p.pid] = False

                min_burst = float('inf')
                process_to_run = None
                
                for p in self.processes:
                    if p.arrival_time <= self.current_time and not is_completed[p.pid]:
                        if p.burst_time < min_burst:
                            min_burst = p.burst_time
                            process_to_run = p
                
                if process_to_run is not None:
                    p = process_to_run
                    
                    for _ in range(p.burst_time):
                        while self.is_paused and self.is_running:
                            time.sleep(0.1)
                        if not self.is_running: return
                        
                        p.remaining_time -= 1
                        self.current_time += 1
                        
                        if self.gantt_chart and self.gantt_chart[-1][0] == p.pid:
                            pid, s, e = self.gantt_chart[-1]
                            self.gantt_chart[-1] = (pid, s, self.current_time)
                        else:
                            self.gantt_chart.append((p.pid, self.current_time - 1, self.current_time))
                        
                        self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                        time.sleep(1)
                    
                    p.completion_time = self.current_time
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    is_completed[p.pid] = True
                    completed += 1
                    self._notify("on_process_complete", p)
                else:
                    time.sleep(1)
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})

    def _run_priority_non_preemptive_live(self):
            """Priority Non-Preemptive with 1-second ticks (Dynamically Patched)"""
            is_completed = {p.pid: False for p in self.processes}
            completed = 0
            
            while completed < len(self.processes) and self.is_running:
                for p in self.processes:
                    if p.pid not in is_completed:
                        is_completed[p.pid] = False

                highest_priority = float('inf')
                process_to_run = None
                
                for p in self.processes:
                    if p.arrival_time <= self.current_time and not is_completed[p.pid]:
                        if p.priority < highest_priority:
                            highest_priority = p.priority
                            process_to_run = p
                
                if process_to_run is not None:
                    p = process_to_run
                    
                    for _ in range(p.burst_time):
                        while self.is_paused and self.is_running:
                            time.sleep(0.1)
                        if not self.is_running: return
                        
                        p.remaining_time -= 1
                        self.current_time += 1
                        
                        if self.gantt_chart and self.gantt_chart[-1][0] == p.pid:
                            pid, s, e = self.gantt_chart[-1]
                            self.gantt_chart[-1] = (pid, s, self.current_time)
                        else:
                            self.gantt_chart.append((p.pid, self.current_time - 1, self.current_time))
                        
                        self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
                        time.sleep(1)
                    
                    p.completion_time = self.current_time
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    is_completed[p.pid] = True
                    completed += 1
                    self._notify("on_process_complete", p)
                else:
                    time.sleep(1)
                    self.current_time += 1
                    self._notify("on_tick", {"time": self.current_time, "processes": self.processes})
    # ============ Control Methods ============
    def pause(self):
        """Pause live execution"""
        self.is_paused = True
    
    def resume(self):
        """Resume live execution"""
        self.is_paused = False
    
    def stop(self):
        """Stop live execution"""
        self.is_running = False
    
    # ============ Results ============
    def get_results(self) -> Dict[str, Any]:
        """Get final results after scheduling"""
        if not self.processes:
            return {}
        
        total_wt = sum(p.waiting_time for p in self.processes)
        total_tat = sum(p.turnaround_time for p in self.processes)
        n = len(self.processes)
        
        return {
            "processes": self.processes,
            "gantt_chart": self.gantt_chart,
            "average_waiting_time": total_wt / n,
            "average_turnaround_time": total_tat / n,
            "current_time": self.current_time
        }
    
    def get_remaining_burst_times(self) -> Dict[int, int]:
        """Get remaining burst times for live display"""
        return {p.pid: p.remaining_time for p in self.processes}
    
    def get_processes_summary(self) -> List[Dict]:
        """Get process summary for GUI display"""
        return [
            {
                "pid": p.pid,
                "arrival_time": p.arrival_time,
                "burst_time": p.burst_time,
                "priority": p.priority,
                "remaining_time": p.remaining_time,
                "waiting_time": p.waiting_time,
                "turnaround_time": p.turnaround_time,
                "completion_time": p.completion_time
            }
            for p in self.processes
        ]
