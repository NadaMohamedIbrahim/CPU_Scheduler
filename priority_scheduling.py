from process import Process

# Unified Run Function
def run(processes, **kwargs):
    mode = kwargs.get("mode", "non_preemptive")

    if mode == "non_preemptive":
        return non_preemptive(processes)
    elif mode == "preemptive":
        return preemptive(processes)
    else:
        raise ValueError("Mode must be 'non_preemptive' or 'preemptive'")

# Non-Preemptive Priority
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
            p.remaining_time = 0

            visited[idx] = True
            completed += 1
        else:
            current_time += 1

    return processes, gantt_chart

# Preemptive Priority
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