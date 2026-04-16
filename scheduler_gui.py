import sys
import copy
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from scheduler_manager import SchedulerManager, SchedulerType
from process import Process


class LiveExecutionThread(QThread):
    """Thread for running live scheduling without freezing GUI"""
    tick_signal = pyqtSignal(dict)
    process_complete_signal = pyqtSignal(object)
    complete_signal = pyqtSignal(dict)
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
    def run(self):
        # Register callbacks to emit signals
        self.manager.register_callback("on_tick", lambda data: self.tick_signal.emit(data))
        self.manager.register_callback("on_process_complete", lambda p: self.process_complete_signal.emit(p))
        self.manager.register_callback("on_complete", lambda data: self.complete_signal.emit(data))
        
        # Execute live scheduling
        self.manager.execute_live()


class SchedulerWindow(QtWidgets.QMainWindow):
    def __init__(self, scheduler_type, title):
        super().__init__()
        self.scheduler_type = scheduler_type
        self.title = title
        self.manager = SchedulerManager()
        self.manager.set_scheduler(scheduler_type)
        
        self.processes_data = []  # Store initial process data
        self.live_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget and main horizontal layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        
        # Left panel (Inputs and Controls)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel (Visualization)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
    def create_left_panel(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # === Input Section ===
        input_group = QtWidgets.QGroupBox("Process Input")
        input_layout = QtWidgets.QFormLayout(input_group)
        
        # Number of processes
        self.num_processes_input = QtWidgets.QSpinBox()
        self.num_processes_input.setRange(1, 20)
        self.num_processes_input.valueChanged.connect(self.generate_process_inputs)
        input_layout.addRow("Number of Processes:", self.num_processes_input)
        
        # Process inputs container
        self.process_inputs_container = QtWidgets.QWidget()
        self.process_inputs_layout = QtWidgets.QVBoxLayout(self.process_inputs_container)
        input_layout.addRow(self.process_inputs_container)
        
        # Time Quantum (only for Round Robin)
        self.quantum_input = QtWidgets.QSpinBox()
        self.quantum_input.setRange(1, 100)
        self.quantum_input.setValue(2)
        if self.scheduler_type == SchedulerType.ROUND_ROBIN:
            input_layout.addRow("Time Quantum:", self.quantum_input)
        
        # Generate button
        self.generate_btn = QtWidgets.QPushButton("Generate Process Table")
        self.generate_btn.clicked.connect(self.generate_process_table)
        input_layout.addRow(self.generate_btn)
        
        layout.addWidget(input_group)
        
        # === Process Table ===
        table_group = QtWidgets.QGroupBox("Processes")
        table_layout = QtWidgets.QVBoxLayout(table_group)
        
        self.process_table = QtWidgets.QTableWidget()
        self.process_table.setColumnCount(5)
        headers = ["PID", "Arrival Time", "Burst Time", "Priority", "Remaining"]
        self.process_table.setHorizontalHeaderLabels(headers)
        self.process_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.process_table)
        
        layout.addWidget(table_group)
        
        # === Control Buttons ===
        control_group = QtWidgets.QGroupBox("Execution Control")
        control_layout = QtWidgets.QVBoxLayout(control_group)
        
        # Live mode checkbox
        self.live_checkbox = QtWidgets.QCheckBox("Live Mode (1 sec = 1 time unit)")
        self.live_checkbox.setChecked(True)
        control_layout.addWidget(self.live_checkbox)
        
        # Button row
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.clicked.connect(self.start_scheduling)
        self.start_btn.setStyleSheet("background-color: #4CAF50;")
        btn_layout.addWidget(self.start_btn)
        
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_scheduling)
        self.pause_btn.setEnabled(False)
        btn_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_scheduling)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        control_layout.addLayout(btn_layout)
        layout.addWidget(control_group)
        
        # === Dynamic Process Addition ===
        dynamic_group = QtWidgets.QGroupBox("Add Process Dynamically (Live Mode)")
        dynamic_layout = QtWidgets.QFormLayout(dynamic_group)
        
        self.new_pid_input = QtWidgets.QSpinBox()
        self.new_pid_input.setRange(0, 999)
        dynamic_layout.addRow("PID:", self.new_pid_input)
        
        self.new_arrival_input = QtWidgets.QSpinBox()
        self.new_arrival_input.setRange(0, 999)
        dynamic_layout.addRow("Arrival Time:", self.new_arrival_input)
        
        self.new_burst_input = QtWidgets.QSpinBox()
        self.new_burst_input.setRange(1, 999)
        dynamic_layout.addRow("Burst Time:", self.new_burst_input)
        
        # Priority input (conditional)
        self.new_priority_input = QtWidgets.QSpinBox()
        self.new_priority_input.setRange(0, 999)
        if "Priority" in self.title:
            dynamic_layout.addRow("Priority:", self.new_priority_input)
        else:
            self.new_priority_input.setVisible(False)
        
        self.add_process_btn = QtWidgets.QPushButton("Add Process")
        self.add_process_btn.clicked.connect(self.add_dynamic_process)
        self.add_process_btn.setEnabled(False)  # Enabled only when running
        dynamic_layout.addRow(self.add_process_btn)
        
        layout.addWidget(dynamic_group)
        
        # === Metrics ===
        metrics_group = QtWidgets.QGroupBox("Results")
        metrics_layout = QtWidgets.QFormLayout(metrics_group)
        
        self.avg_wt_label = QtWidgets.QLabel("-")
        metrics_layout.addRow("Average Waiting Time:", self.avg_wt_label)
        
        self.avg_tat_label = QtWidgets.QLabel("-")
        metrics_layout.addRow("Average Turnaround Time:", self.avg_tat_label)
        
        self.elapsed_time_label = QtWidgets.QLabel("0")
        metrics_layout.addRow("Elapsed Time:", self.elapsed_time_label)
        
        layout.addWidget(metrics_group)
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # === Gantt Chart ===
        gantt_group = QtWidgets.QGroupBox("Gantt Chart")
        gantt_layout = QtWidgets.QVBoxLayout(gantt_group)
        
        self.figure = Figure(figsize=(8, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(200)
        gantt_layout.addWidget(self.canvas)
        
        toolbar = NavigationToolbar(self.canvas, self)
        gantt_layout.addWidget(toolbar)
        
        layout.addWidget(gantt_group)
        
        # === Remaining Burst Time Table ===
        remaining_group = QtWidgets.QGroupBox("Remaining Burst Times (Live)")
        remaining_layout = QtWidgets.QVBoxLayout(remaining_group)
        
        self.remaining_table = QtWidgets.QTableWidget()
        self.remaining_table.setColumnCount(3)
        self.remaining_table.setHorizontalHeaderLabels(["PID", "Burst Time", "Remaining"])
        self.remaining_table.horizontalHeader().setStretchLastSection(True)
        remaining_layout.addWidget(self.remaining_table)
        
        layout.addWidget(remaining_group)
        
        return panel
    
    def generate_process_inputs(self):
        """Generate input fields based on number of processes"""
        # Clear existing
        while self.process_inputs_layout.count():
            item = self.process_inputs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        n = self.num_processes_input.value()
        
        # Create scroll area for many processes
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        
        container = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(container)
        
        # Headers
        layout.addWidget(QtWidgets.QLabel("PID"), 0, 0)
        layout.addWidget(QtWidgets.QLabel("Arrival"), 0, 1)
        layout.addWidget(QtWidgets.QLabel("Burst"), 0, 2)
        if "Priority" in self.title:
            layout.addWidget(QtWidgets.QLabel("Priority"), 0, 3)
        
        self.input_fields = []
        
        for i in range(n):
            row = i + 1
            pid_input = QtWidgets.QSpinBox()
            pid_input.setValue(i)
            pid_input.setRange(0, 999)
            layout.addWidget(pid_input, row, 0)
            
            arrival_input = QtWidgets.QSpinBox()
            arrival_input.setValue(0)
            arrival_input.setRange(0, 999)
            layout.addWidget(arrival_input, row, 1)
            
            burst_input = QtWidgets.QSpinBox()
            burst_input.setValue(1)
            burst_input.setRange(1, 999)
            layout.addWidget(burst_input, row, 2)
            
            fields = [pid_input, arrival_input, burst_input]
            
            if "Priority" in self.title:
                priority_input = QtWidgets.QSpinBox()
                priority_input.setValue(0)
                priority_input.setRange(0, 999)
                layout.addWidget(priority_input, row, 3)
                fields.append(priority_input)
            
            self.input_fields.append(fields)
        
        scroll.setWidget(container)
        self.process_inputs_layout.addWidget(scroll)
    
    def generate_process_table(self):
        """Populate the process table from inputs"""
        self.processes_data = []
        self.process_table.setRowCount(0)
        
        for fields in self.input_fields:
            pid = fields[0].value()
            arrival = fields[1].value()
            burst = fields[2].value()
            priority = fields[3].value() if len(fields) > 3 else None
            
            self.processes_data.append({
                'pid': pid,
                'arrival': arrival,
                'burst': burst,
                'priority': priority
            })
            
            row = self.process_table.rowCount()
            self.process_table.insertRow(row)
            self.process_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(pid)))
            self.process_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(arrival)))
            self.process_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(burst)))
            self.process_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(priority) if priority is not None else "-"))
            self.process_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(burst)))
        
        # Set quantum if Round Robin
        if self.scheduler_type == SchedulerType.ROUND_ROBIN:
            self.manager.time_quantum = self.quantum_input.value()
    
    def start_scheduling(self):
        """Start the scheduling execution"""
        if not self.processes_data:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please generate processes first!")
            return
        
        # Reset manager
        self.manager.reset()
        self.manager.set_scheduler(self.scheduler_type)
        
        if self.scheduler_type == SchedulerType.ROUND_ROBIN:
            self.manager.time_quantum = self.quantum_input.value()
        
        # Add processes to manager
        for p_data in self.processes_data:
            self.manager.add_process(
                pid=p_data['pid'],
                arrival_time=p_data['arrival'],
                burst_time=p_data['burst'],
                priority=p_data['priority']
            )
        
        # Clear previous Gantt
        self.figure.clear()
        self.canvas.draw()
        
        # Reset tables
        self.update_remaining_table()
        
        if self.live_checkbox.isChecked():
            # Live mode
            self.start_live_mode()
        else:
            # Static mode
            self.start_static_mode()
    
    def start_live_mode(self):
        """Execute in live mode with 1-second ticks"""
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.add_process_btn.setEnabled(True)
        
        self.live_thread = LiveExecutionThread(self.manager)
        self.live_thread.tick_signal.connect(self.on_live_tick)
        self.live_thread.process_complete_signal.connect(self.on_process_complete)
        self.live_thread.complete_signal.connect(self.on_scheduling_complete)
        self.live_thread.start()
    
    def start_static_mode(self):
        """Execute instantly and show final results"""
        results = self.manager.execute_batch()
        self.display_results(results)
        self.draw_gantt_chart(results['gantt_chart'], live=False)
    
    def on_live_tick(self, data):
        """Handle live update tick"""
        current_time = data['time']
        self.elapsed_time_label.setText(str(current_time))
        
        # Update remaining burst table
        self.update_remaining_table()
        
        # Update Gantt chart incrementally
        if self.manager.gantt_chart:
            self.draw_gantt_chart(self.manager.gantt_chart, live=True)
    
    def on_process_complete(self, process):
        """Handle process completion in live mode"""
        # Update process table
        for row in range(self.process_table.rowCount()):
            if self.process_table.item(row, 0).text() == str(process.pid):
                self.process_table.item(row, 4).setText("0")
                break
    
    def on_scheduling_complete(self, results):
        """Handle scheduling completion"""
        self.display_results(results)
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.add_process_btn.setEnabled(False)
        
        # Final Gantt draw
        self.draw_gantt_chart(results['gantt_chart'], live=False)
    
    def pause_scheduling(self):
        """Pause/Resume live execution"""
        if self.manager.is_paused:
            self.manager.resume()
            self.pause_btn.setText("Pause")
        else:
            self.manager.pause()
            self.pause_btn.setText("Resume")
    
    def stop_scheduling(self):
        """Stop live execution"""
        self.manager.stop()
        if self.live_thread and self.live_thread.isRunning():
            self.live_thread.wait(1000)
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.add_process_btn.setEnabled(False)
    
    def add_dynamic_process(self):
        """Add a new process while running"""
        pid = self.new_pid_input.value()
        arrival = self.new_arrival_input.value()
        burst = self.new_burst_input.value()
        priority = self.new_priority_input.value() if "Priority" in self.title else None
        
        # Check for duplicate PID
        for p in self.manager.processes:
            if p.pid == pid:
                QtWidgets.QMessageBox.warning(self, "Error", f"PID {pid} already exists!")
                return
        
        # Add to manager
        new_process = self.manager.add_process(pid, arrival, burst, priority)
        
        # Add to tables
        row = self.process_table.rowCount()
        self.process_table.insertRow(row)
        self.process_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(pid)))
        self.process_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(arrival)))
        self.process_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(burst)))
        self.process_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(priority) if priority else "-"))
        self.process_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(burst)))
        
        # Clear inputs
        self.new_pid_input.setValue(pid + 1)
        self.new_arrival_input.setValue(0)
        self.new_burst_input.setValue(1)
    
    def update_remaining_table(self):
        """Update the remaining burst time table"""
        self.remaining_table.setRowCount(0)
        
        if not self.manager.processes:
            return
            
        for p in self.manager.processes:
            row = self.remaining_table.rowCount()
            self.remaining_table.insertRow(row)
            self.remaining_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p.pid)))
            self.remaining_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(p.burst_time)))
            self.remaining_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(p.remaining_time)))
    
    def draw_gantt_chart(self, gantt_data, live=True):
        """Draw Gantt chart from scheduling data"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not gantt_data:
            self.canvas.draw()
            return
        
        # Colors for different processes
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B500', '#6C5CE7']
        
        y_pos = 0
        height = 0.4
        
        for i, (pid, start, end) in enumerate(gantt_data):
            duration = end - start
            color = colors[pid % len(colors)]
            
            ax.barh(y_pos, width=duration, left=start, height=height, 
                   color=color, edgecolor='black', alpha=0.8)
            
            # Add text label
            if duration >= 1:
                ax.text(start + duration/2, y_pos, f'P{pid}', 
                       ha='center', va='center', fontweight='bold')
        
        ax.set_xlabel('Time')
        ax.set_title('Gantt Chart')
        ax.set_yticks([])
        ax.grid(axis='x', alpha=0.3)
        
        # Set x-axis to show all time units
        max_time = max(end for _, _, end in gantt_data)
        ax.set_xlim(0, max_time + 1)
        
        self.canvas.draw()
    
    def display_results(self, results):
        """Display final metrics"""
        if 'average_waiting_time' in results:
            self.avg_wt_label.setText(f"{results['average_waiting_time']:.2f}")
        if 'average_turnaround_time' in results:
            self.avg_tat_label.setText(f"{results['average_turnaround_time']:.2f}")
        
        # Update process table with final values
        for p in results['processes']:
            for row in range(self.process_table.rowCount()):
                if self.process_table.item(row, 0).text() == str(p.pid):
                    self.process_table.item(row, 4).setText("0")
                    break
    
    def closeEvent(self, event):
        """Clean up on close"""
        if self.live_thread and self.live_thread.isRunning():
            self.manager.stop()
            self.live_thread.wait(1000)
        event.accept()