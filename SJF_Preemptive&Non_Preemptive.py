class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0

def sjf_non_preemptive(processes):
    time = 0
    completed_processes = 0
    n = len(processes)
    gantt_chart = []
    
    # Track which processes have finished
    is_completed = [False] * n
    
    while completed_processes < n:
        idx_to_run = -1
        min_burst = float('inf')
        
        # Find the process with the minimum burst time among the arrived ones
        for i in range(n):
            if processes[i].arrival_time <= time and not is_completed[i]:
                if processes[i].burst_time < min_burst:
                    min_burst = processes[i].burst_time
                    idx_to_run = i
                # Tie-breaker: If burst times are equal, pick the one that arrived first
                elif processes[i].burst_time == min_burst:
                    if processes[i].arrival_time < processes[idx_to_run].arrival_time:
                        idx_to_run = i
        
        if idx_to_run != -1:
            p = processes[idx_to_run]
            start_time = time
            
            # Execute the process fully
            time += p.burst_time
            p.remaining_time = 0
            
            # Calculate metrics
            p.completion_time = time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            
            # Add to Gantt chart (pid, start, end)
            gantt_chart.append((p.pid, start_time, time))
            
            is_completed[idx_to_run] = True
            completed_processes += 1
        else:
            # CPU is idle, advance time to the next process's arrival
            next_arrival = float('inf')
            for i in range(n):
                if not is_completed[i] and processes[i].arrival_time < next_arrival:
                    next_arrival = processes[i].arrival_time
            time = next_arrival
            
    return processes, gantt_chart



def sjf_preemptive(processes):
    time = 0
    completed_processes = 0
    n = len(processes)
    gantt_chart = []
    
    is_completed = [False] * n
    
    current_pid = None
    start_time = 0
    
    while completed_processes < n:
        idx_to_run = -1
        min_rem_time = float('inf')
        
        # Check all processes to find the one with the shortest remaining time
        for i in range(n):
            if processes[i].arrival_time <= time and not is_completed[i]:
                if processes[i].remaining_time < min_rem_time:
                    min_rem_time = processes[i].remaining_time
                    idx_to_run = i
                elif processes[i].remaining_time == min_rem_time:
                    # Tie-breaker: earlier arrival time
                    if processes[i].arrival_time < processes[idx_to_run].arrival_time:
                        idx_to_run = i
        
        if idx_to_run != -1:
            p = processes[idx_to_run]
            
            # Gantt chart logic: if the running process changes (context switch)
            if current_pid != p.pid:
                if current_pid is not None and time > start_time:
                    # Close out the previous Gantt block before switching
                    gantt_chart.append((current_pid, start_time, time))
                current_pid = p.pid
                start_time = time
            
            # Execute for 1 unit of time
            p.remaining_time -= 1
            time += 1
            
            # If process finishes
            if p.remaining_time == 0:
                is_completed[idx_to_run] = True
                completed_processes += 1
                
                # Calculate metrics
                p.completion_time = time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                
                # Close out its final block on the Gantt chart
                gantt_chart.append((current_pid, start_time, time))
                current_pid = None # Reset so the next process triggers a new start_time
        else:
            # CPU is idle
            if current_pid is not None and time > start_time:
                gantt_chart.append((current_pid, start_time, time))
                current_pid = None
            
            # Jump time to the next process arrival to save loops
            next_arrival = float('inf')
            for i in range(n):
                if not is_completed[i] and processes[i].arrival_time < next_arrival:
                    next_arrival = processes[i].arrival_time
            if next_arrival != float('inf'):
                time = next_arrival
            else:
                time += 1
                
    return processes, gantt_chart


# --- TEST DATA ---
if __name__ == "__main__":
    def get_test_processes():
        return [
            Process(1, 0, 8),
            Process(2, 1, 4),
            Process(3, 2, 9),
            Process(4, 3, 5)
        ]

    # --- TEST NON-PREEMPTIVE ---
    print("--- SJF NON-PREEMPTIVE ---")
    np_result, np_gantt = sjf_non_preemptive(get_test_processes())

    print("Gantt Chart:")
    for block in np_gantt:
        print(f"P{block[0]}: {block[1]} -> {block[2]}")

    print("\nProcess Details:")
    for p in np_result:
        print(f"P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")

    # --- TEST PREEMPTIVE ---
    print("\n--- SJF PREEMPTIVE ---")
    p_result, p_gantt = sjf_preemptive(get_test_processes())

    print("Gantt Chart:")
    for block in p_gantt:
        print(f"P{block[0]}: {block[1]} -> {block[2]}")

    print("\nProcess Details:")
    for p in p_result:
        print(f"P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")
