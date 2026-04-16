"""
test_integration.py - Testing all CPU Scheduling Algorithms
"""

from process import Process
from fcfs import execute_static_fcfs
from priority_scheduling import run as priority_run
from round_robin import run as rr_run
from sjf import sjf_non_preemptive, sjf_preemptive

def print_separator(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_fcfs():
    print_separator("TEST 1: FCFS (First Come First Serve)")
    
    processes = [
        Process(1, 0, 5),
        Process(2, 1, 3),
        Process(3, 2, 8),
        Process(4, 10, 2)
    ]
    
    result = execute_static_fcfs(processes)
    
    print("\n📊 Gantt Chart:")
    for pid, start, end in result['gantt_chart']:
        print(f"   P{pid} | {start} → {end}")
    
    print(f"\n📈 Average Waiting Time: {result['average_waiting_time']:.2f}")
    print(f"📈 Average Turnaround Time: {result['average_turnaround_time']:.2f}")
    
    print("\n📋 Process Details:")
    for p in result['processes']:
        print(f"   P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")

def test_priority_non_preemptive():
    print_separator("TEST 2: Priority Scheduling (Non-Preemptive)")
    print("   Note: Smaller number = Higher Priority")
    
    processes = [
        Process(1, 0, 5, 2),
        Process(2, 1, 3, 1),
        Process(3, 2, 8, 4),
        Process(4, 3, 6, 3)
    ]
    
    result, gantt = priority_run(processes, mode="non_preemptive")
    
    print("\n📊 Gantt Chart:")
    for pid, start, end in gantt:
        print(f"   P{pid} | {start} → {end}")
    
    print("\n📋 Process Details:")
    for p in result:
        print(f"   P{p.pid} (Pri={p.priority}): WT={p.waiting_time}, TAT={p.turnaround_time}")

def test_priority_preemptive():
    print_separator("TEST 3: Priority Scheduling (Preemptive)")
    print("   Note: Smaller number = Higher Priority")
    
    processes = [
        Process(1, 0, 5, 2),
        Process(2, 1, 3, 1),
        Process(3, 2, 8, 4),
        Process(4, 3, 6, 3)
    ]
    
    result, gantt = priority_run(processes, mode="preemptive")
    
    print("\n📊 Gantt Chart:")
    for pid, start, end in gantt:
        print(f"   P{pid} | {start} → {end}")
    
    print("\n📋 Process Details:")
    for p in result:
        print(f"   P{p.pid} (Pri={p.priority}): WT={p.waiting_time}, TAT={p.turnaround_time}")

def test_round_robin():
    print_separator("TEST 4: Round Robin (Time Quantum = 2)")
    
    processes = [
        Process(1, 0, 5),
        Process(2, 1, 3),
        Process(3, 2, 8)
    ]
    
    gantt, avg_wt, avg_tat = rr_run(processes, 2)
    
    print("\n📊 Gantt Chart:")
    for pid, start, end in gantt:
        print(f"   P{pid} | {start} → {end}")
    
    print(f"\n📈 Average Waiting Time: {avg_wt:.2f}")
    print(f"📈 Average Turnaround Time: {avg_tat:.2f}")

def test_sjf_non_preemptive():
    print_separator("TEST 5: SJF Non-Preemptive (Shortest Job First)")
    
    processes = [
        Process(1, 0, 8),
        Process(2, 1, 4),
        Process(3, 2, 9),
        Process(4, 3, 5)
    ]
    
    result, gantt = sjf_non_preemptive(processes)
    
    print("\n📊 Gantt Chart:")
    for pid, start, end in gantt:
        print(f"   P{pid} | {start} → {end}")
    
    print("\n📋 Process Details:")
    for p in result:
        print(f"   P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")

def test_sjf_preemptive():
    print_separator("TEST 6: SJF Preemptive (Shortest Remaining Time First)")
    
    processes = [
        Process(1, 0, 8),
        Process(2, 1, 4),
        Process(3, 2, 9),
        Process(4, 3, 5)
    ]
    
    result, gantt = sjf_preemptive(processes)
    
    print("\n📊 Gantt Chart:")
    for pid, start, end in gantt:
        print(f"   P{pid} | {start} → {end}")
    
    print("\n📋 Process Details:")
    for p in result:
        print(f"   P{p.pid}: WT={p.waiting_time}, TAT={p.turnaround_time}")

# Run all tests
if __name__ == "__main__":
    print("\n" + "🎯" * 30)
    print("   CPU SCHEDULING ALGORITHMS TEST SUITE")
    print("🎯" * 30)
    
    tests = [
        ("FCFS", test_fcfs),
        ("Priority Non-Preemptive", test_priority_non_preemptive),
        ("Priority Preemptive", test_priority_preemptive),
        ("Round Robin", test_round_robin),
        ("SJF Non-Preemptive", test_sjf_non_preemptive),
        ("SJF Preemptive", test_sjf_preemptive)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
    
    print_separator("ALL TESTS COMPLETED")