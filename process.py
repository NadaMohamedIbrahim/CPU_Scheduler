class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority  # Used only for Priority scheduling (lower number = higher priority)
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.first_execution_time = None  # For response time calculation (optional)
        
    def reset(self):
        """Reset process metrics for re-run"""
        self.remaining_time = self.burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.first_execution_time = None
        
    def __str__(self):
        return f"P{self.pid} | AT:{self.arrival_time} | BT:{self.burst_time} | Rem:{self.remaining_time} | Pri:{self.priority}"