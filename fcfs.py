from process import Process

def run_fcfs(processes, **kwargs):
    # Sort processes by arrival time to ensure FCFS order
    processes.sort(key=lambda x: (x.arrival_time, x.pid))
    
    current_time = 0
    gantt_chart = []
    
    for p in processes:
        # Fast-forward time if the CPU is idle waiting for the next process
        if current_time < p.arrival_time:
            current_time = p.arrival_time
            
        start_time = current_time
        current_time += p.burst_time
        end_time = current_time
        
        # Calculate individual process metrics
        p.completion_time = end_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.remaining_time = 0  # Process is complete
        
        # Append to Gantt chart 
        gantt_chart.append((p.pid, start_time, end_time))
        
    return processes, gantt_chart

def calculate_average_metrics(processes):
    if not processes:
        return 0, 0
        
    total_wt = sum(p.waiting_time for p in processes)
    total_tat = sum(p.turnaround_time for p in processes)
    n = len(processes)
    
    return total_wt / n, total_tat / n

def execute_static_fcfs(processes):
    """The Static Run Mode handler. 
    Runs the algorithm instantly and returns all finalized data for the GUI."""
    # Run the FCFS algorithm
    updated_processes, gantt_chart = run_fcfs(processes)
    
    # Calculate overall averages
    avg_wt, avg_tat = calculate_average_metrics(updated_processes)
    
    return {
        "processes": updated_processes,
        "gantt_chart": gantt_chart,
        "average_waiting_time": avg_wt,
        "average_turnaround_time": avg_tat
    }