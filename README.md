# 🖥️ CPU Scheduler 

A graphical user interface (GUI) desktop application built to simulate, visualize, and analyze CPU scheduling algorithms. 

---

## 🚀 Features

* **Live Execution Mode:** The scheduler operates in real-time, with each 1 unit of algorithmic time explicitly mapped to 1 real-world second.
* **Static Execution Mode:** Provides an option to run and analyze the currently existing processes instantly, bypassing the live scheduling delay.
* **Dynamic Process Insertion:** A new process can be added dynamically while the live scheduler is actively running.
* **Smart UI Inputs:** The application dynamically adapts its forms and will not ask the user for unused info based on the selected algorithm.
* **Live Visualizations:** Features a timeline (Gantt Chart) showing the order and time taken by each process, drawn live as the scheduler runs.
* **Real-Time Metrics:** Displays a remaining burst time table that is updated live, alongside the final calculation of the average waiting time and turnaround time.

---

## 🧠 Supported Schedulers

The system implements the following algorithms:
1. **FCFS** (First-Come, First-Served)
2. **SJF** (Shortest Job First) — *Preemptive and Non-Preemptive*
3. **Priority Scheduling** — *Preemptive and Non-Preemptive* (the smaller the priority number, the higher the priority)
4. **Round Robin**

---
