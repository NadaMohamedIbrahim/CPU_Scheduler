# ================================
# Process Class (Given Template)
# ================================
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


# ================================
# Unified Run Function (TEMPLATE)
# ================================
def run(processes, **kwargs):
    mode = kwargs.get("mode", "non_preemptive")

    if mode == "non_preemptive":
        return non_preemptive(processes)
    elif mode == "preemptive":
        return preemptive(processes)
    else:
        raise ValueError("Mode must be 'non_preemptive' or 'preemptive'")


# ================================
# Non-Preemptive Priority
# ================================
def non_preemptive(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    visited = [False] * n
    gantt_chart = []

    while completed < n:
        idx = -1
        highest_priority = float('inf')

        for i in range(n):
            if processes[i].arrival_time <= current_time and not visited[i]:
                if processes[i].priority < highest_priority:
                    highest_priority = processes[i].priority
                    idx = i
                elif processes[i].priority == highest_priority:
                    if processes[i].arrival_time < processes[idx].arrival_time:
                        idx = i

        if idx != -1:
            p = processes[idx]

            start = current_time
            end = current_time + p.burst_time
            gantt_chart.append((p.pid, start, end))

            current_time = end
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time

            visited[idx] = True
            completed += 1
        else:
            current_time += 1

    return processes, gantt_chart


# ================================
# Preemptive Priority
# ================================
def preemptive(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    gantt_chart = []
    last_pid = -1

    while completed < n:
        idx = -1
        highest_priority = float('inf')

        for i in range(n):
            if processes[i].arrival_time <= current_time and processes[i].remaining_time > 0:
                if processes[i].priority < highest_priority:
                    highest_priority = processes[i].priority
                    idx = i
                elif processes[i].priority == highest_priority:
                    if processes[i].arrival_time < processes[idx].arrival_time:
                        idx = i

        if idx != -1:
            p = processes[idx]

            # Gantt handling
            if last_pid != p.pid:
                gantt_chart.append((p.pid, current_time, current_time + 1))
            else:
                pid, start, end = gantt_chart[-1]
                gantt_chart[-1] = (pid, start, end + 1)

            last_pid = p.pid

            # Execute 1 unit
            p.remaining_time -= 1
            current_time += 1

            if p.remaining_time == 0:
                completed += 1
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
        else:
            current_time += 1
            last_pid = -1

    return processes, gantt_chart


# ================================
# Helper: Print Results
# ================================
def print_results(processes, gantt, title):
    print(f"\n=== {title} ===")
    print("PID\tAT\tBT\tPR\tCT\tTAT\tWT")

    for p in processes:
        print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.priority}\t"
              f"{p.completion_time}\t{p.turnaround_time}\t{p.waiting_time}")

    print("Gantt Chart:")
    print(gantt)


# ================================
# Main (Test)
# ================================
if __name__ == "__main__":

    process_list = [
        Process(1, 0, 5, 2),
        Process(2, 1, 3, 1),
        Process(3, 2, 8, 4),
        Process(4, 3, 6, 3),
    ]

    # Non-preemptive
    result1, gantt1 = run(
        [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in process_list],
        mode="non_preemptive"
    )
    print_results(result1, gantt1, "Non-Preemptive Priority")

    # Preemptive
    result2, gantt2 = run(
        [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in process_list],
        mode="preemptive"
    )
    print_results(result2, gantt2, "Preemptive Priority")