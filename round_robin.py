from collections import deque
from process import Process

def run(processes, time_quantum):
    time = 0
    queue = deque()
    gantt_chart = []

    processes.sort(key=lambda x: x.arrival_time)
    n = len(processes)
    i = 0  # index for processes

    while queue or i < n:
        # add arrived processes to queue
        while i < n and processes[i].arrival_time <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time = processes[i].arrival_time
            continue

        current = queue.popleft()

        exec_time = min(time_quantum, current.remaining_time)
        start_time = time
        time += exec_time
        current.remaining_time -= exec_time

        gantt_chart.append((current.pid, start_time, time))

        # add newly arrived processes
        while i < n and processes[i].arrival_time <= time:
            queue.append(processes[i])
            i += 1

        if current.remaining_time > 0:
            queue.append(current)
        else:
            current.completion_time = time
            current.turnaround_time = current.completion_time - current.arrival_time
            current.waiting_time = current.turnaround_time - current.burst_time

    total_wt = 0
    total_tat = 0

    for p in processes:
        total_wt += p.waiting_time
        total_tat += p.turnaround_time

    avg_wt = total_wt / len(processes)
    avg_tat = total_tat / len(processes)        

    return gantt_chart, avg_wt, avg_tat