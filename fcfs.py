class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority

        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        
    def __str__(self):
         #A helper to print the process details cleanly during testing
        return f"PID: {self.pid} | WT: {self.waiting_time} | TAT: {self.turnaround_time}"


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
    """
    The Static Run Mode handler. 
    Runs the algorithm instantly and returns all finalized data for the GUI.
    """
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


  
#test 
#if __name__ == "__main__":
    # Create the test input
    #process_list = [
        #Process(1, 0, 5),
        #Process(2, 1, 3),
        #Process(3, 2, 8),
        #Process(4, 10, 2) # Adding a gap to test idle CPU time
    ]
    
    # Execute the static run
    #results = execute_static_fcfs(process_list)
    
    # Output the results
    #print("--- Gantt Chart ---")
    #print(results["gantt_chart"])
    
    #print("\n--- Process Metrics ---")
    #for p in results["processes"]:
        #print(p)
        
    #print("\n--- System Averages ---")
    #print(f"Average Waiting Time: {results['average_waiting_time']}")
    #print(f"Average Turnaround Time: {results['average_turnaround_time']}")
