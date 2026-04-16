"""
test_manager_input.py - Test Scheduler Manager with User Input
You can configure everything from the terminal
"""

from scheduler_manager import SchedulerManager, SchedulerType

def get_scheduler_from_user():
    """Let user choose the scheduler type"""
    print("\n📋 Available Scheduler Types:")
    print("1. FCFS")
    print("2. SJF Non-Preemptive")
    print("3. SJF Preemptive")
    print("4. Priority Non-Preemptive")
    print("5. Priority Preemptive")
    print("6. Round Robin")
    
    choice = input("\nChoose scheduler (1-6): ")
    
    schedulers = {
        "1": SchedulerType.FCFS,
        "2": SchedulerType.SJF_NON_PREEMPTIVE,
        "3": SchedulerType.SJF_PREEMPTIVE,
        "4": SchedulerType.PRIORITY_NON_PREEMPTIVE,
        "5": SchedulerType.PRIORITY_PREEMPTIVE,
        "6": SchedulerType.ROUND_ROBIN,
    }
    
    return schedulers.get(choice, SchedulerType.FCFS)

def get_processes_from_user():
    """Let user enter processes"""
    processes = []
    print("\n📝 Enter Process Information")
    print("(Enter 'done' when finished)")
    
    pid = 1
    while True:
        print(f"\n--- Process {pid} ---")
        arrival = input("Arrival Time: ")
        if arrival.lower() == 'done':
            break
        
        burst = input("Burst Time: ")
        if burst.lower() == 'done':
            break
        
        # Only ask for priority if needed
        priority = None
        ask_priority = input("Need Priority? (y/n): ")
        if ask_priority.lower() == 'y':
            priority = int(input("Priority (lower number = higher priority): "))
        
        processes.append({
            "pid": pid,
            "arrival_time": int(arrival),
            "burst_time": int(burst),
            "priority": priority
        })
        pid += 1
    
    return processes

def get_mode_from_user():
    """Let user choose batch or live mode"""
    print("\n🎮 Execution Mode:")
    print("1. Batch Mode (runs instantly)")
    print("2. Live Mode (1 second = 1 time unit)")
    
    choice = input("Choose (1-2): ")
    return choice == "2"  # True for live, False for batch

def get_time_quantum():
    """Get time quantum for Round Robin"""
    quantum = input("Enter Time Quantum for Round Robin (default 2): ")
    return int(quantum) if quantum else 2

def main():
    print("=" * 60)
    print("🎯 CPU SCHEDULER MANAGER - INTERACTIVE TEST")
    print("=" * 60)
    
    # Create manager
    manager = SchedulerManager()
    
    # 1. Get scheduler type
    scheduler = get_scheduler_from_user()
    print(f"\n✅ Selected: {scheduler.value}")
    
    # 2. Get time quantum if Round Robin
    time_quantum = None
    if scheduler == SchedulerType.ROUND_ROBIN:
        time_quantum = get_time_quantum()
        manager.set_scheduler(scheduler, time_quantum=time_quantum)
    else:
        manager.set_scheduler(scheduler)
    
    # 3. Get processes
    processes = get_processes_from_user()
    if not processes:
        print("❌ No processes entered. Exiting.")
        return
    
    manager.add_processes_batch(processes)
    print(f"\n✅ Loaded {len(processes)} processes")
    
    # 4. Get execution mode
    is_live = get_mode_from_user()
    
    # 5. Define callback to see updates
    def on_tick(data):
        print(f"⏰ Time: {data['time']} | Remaining: {manager.get_remaining_burst_times()}")
    
    def on_complete(result):
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        print(f"Gantt Chart: {result['gantt_chart']}")
        print(f"Average Waiting Time: {result['average_waiting_time']:.2f}")
        print(f"Average Turnaround Time: {result['average_turnaround_time']:.2f}")
        print("\n📋 Process Details:")
        for p in result['processes']:
            print(f"  P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")
    
    # Register callbacks
    manager.register_callback("on_tick", on_tick)
    manager.register_callback("on_complete", on_complete)
    
    # 6. Run
    if is_live:
        print("\n🚀 Running in LIVE MODE (Ctrl+C to stop)")
        manager.execute_live()
        
        try:
            # Keep running until user interrupts
            while manager.is_running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping...")
            manager.stop()
    else:
        print("\n🚀 Running in BATCH MODE...")
        result = manager.execute_batch()
        on_complete(result)

if __name__ == "__main__":
    main()