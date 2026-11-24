# OS Nexus – Operating System Resource Manager

## Project Overview
OS Nexus is a web-based Operating System Resource Manager designed to demonstrate important OS concepts through interactive simulations and real-time system monitoring.

## Features

### 1. System Monitoring
- CPU usage monitoring
- Memory usage monitoring
- Disk usage information
- System information

### 2. CPU Scheduling
- First Come First Serve (FCFS)
- Shortest Job First (SJF)
- Priority Scheduling
- Round Robin

### 3. Memory Management
- First Fit
- Best Fit
- Worst Fit

### 4. Deadlock Safety Analysis
- Banker's Algorithm
- Need Matrix calculation
- Safe sequence identification
- Safe/Unsafe state detection

### 5. Disk Scheduling
- FCFS
- SSTF
- SCAN
- C-SCAN
- Total head movement
- Average seek movement

## Technologies Used
- Python
- Flask
- HTML
- CSS
- JavaScript
- psutil

## Project Structure

```text
OS_Nexus_Capstone/
│
├── app.py
├── modules.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   └── js/
│       └── app.js
├── venv/
└── README.md
```

## Installation and Execution

1. Clone or download the project.
2. Open the project directory.
3. Create and activate a virtual environment.
4. Install dependencies:

```bash
pip install flask psutil
```

5. Run the application:

```bash
python3 app.py
```

6. Open the browser:

```text
http://127.0.0.1:5001
```

## Objective
To provide an interactive platform for understanding and visualizing fundamental operating system algorithms and resource management techniques.

## Conclusion
OS Nexus combines theoretical operating system concepts with practical simulations, helping users understand CPU scheduling, memory allocation, deadlock safety, and disk scheduling through an interactive dashboard.