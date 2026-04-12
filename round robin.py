from collections import deque

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0


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

    return processes, gantt_chart

# test
# ex1

# process_list = [
#     Process(1, 0, 5),
#     Process(2, 1, 3),
#     Process(3, 2, 8),
#     Process(4, 3, 6)
# ]

# ex2 _ same arrival time

# process_list = [
#     Process(1, 0, 4),
#     Process(2, 0, 3),
#     Process(3, 0, 2)
# ]

# ex3 _ a process arrives late 

# process_list = [
#     Process(1, 0, 4),
#     Process(2, 5, 3)
# ]

# ex4

# process_list = [
#     Process(1, 0, 4)
# ]    

# time_quantum = 2 # 1, 10

# result, gantt = run(process_list, time_quantum)

# print("Gantt Chart:")
# for p in gantt:
#     print(f"P{p[0]}: {p[1]} -> {p[2]}")

# print("\nProcess Details:")
# for p in result:
#     print(f"P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")