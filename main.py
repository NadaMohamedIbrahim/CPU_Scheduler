import sys
from PyQt5 import QtWidgets, QtCore
from scheduler_gui import SchedulerWindow
from scheduler_manager import SchedulerType


class MainLauncher(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduler")
        self.setGeometry(100, 100, 400, 500)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        title = QtWidgets.QLabel("CPU Scheduling Algorithms")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Define scheduler buttons with their types
        schedulers = [
            ("FCFS", SchedulerType.FCFS),
            ("SJF Non-Preemptive", SchedulerType.SJF_NON_PREEMPTIVE),
            ("SJF Preemptive (SRTF)", SchedulerType.SJF_PREEMPTIVE),
            ("Priority Non-Preemptive", SchedulerType.PRIORITY_NON_PREEMPTIVE),
            ("Priority Preemptive", SchedulerType.PRIORITY_PREEMPTIVE),
            ("Round Robin", SchedulerType.ROUND_ROBIN),
        ]
        
        for name, sched_type in schedulers:
            btn = QtWidgets.QPushButton(name)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            btn.clicked.connect(lambda checked, t=sched_type, n=name: self.open_scheduler(t, n))
            layout.addWidget(btn)
        
        layout.addStretch()
    
    def open_scheduler(self, sched_type, name):
        self.window = SchedulerWindow(sched_type, name)
        self.window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application-wide stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            color: #333;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        QPushButton {
            padding: 8px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QTableWidget {
            border: 1px solid #ddd;
            gridline-color: #ddd;
        }
        QHeaderView::section {
            background-color: #4CAF50;
            color: white;
            padding: 5px;
            border: none;
        }
    """)
    
    launcher = MainLauncher()
    launcher.show()
    sys.exit(app.exec_())