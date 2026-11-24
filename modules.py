
"""
OS NEXUS - Operating System Resource Management Simulator
Core algorithms:
1. CPU Scheduling
2. Memory Management
3. Banker's Algorithm (Deadlock Avoidance)
4. Disk Scheduling
"""

from collections import deque


# =========================================================
# 1. CPU SCHEDULING
# =========================================================

def cpu_scheduling(processes, algorithm="FCFS", quantum=2):

    if not processes:
        raise ValueError("At least one process is required.")

    jobs = []

    for p in processes:
        pid = str(p["pid"])
        arrival = int(p.get("arrival_time", 0))
        burst = int(p["burst_time"])
        priority = int(p.get("priority", 1))

        if arrival < 0 or burst <= 0:
            raise ValueError("Arrival must be >= 0 and burst must be > 0.")

        jobs.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "priority": priority
        })

    if len({p["pid"] for p in jobs}) != len(jobs):
        raise ValueError("Process IDs must be unique.")

    algorithm = algorithm.upper()

    if algorithm not in ["FCFS", "SJF", "PRIORITY", "ROUND ROBIN"]:
        raise ValueError("Invalid CPU scheduling algorithm.")

    if algorithm == "ROUND ROBIN" and quantum <= 0:
        raise ValueError("Time quantum must be positive.")

    remaining = {p["pid"]: p["burst"] for p in jobs}
    completed = {}
    gantt = []
    current_time = 0

    # ---------- FCFS, SJF, PRIORITY ----------

    if algorithm != "ROUND ROBIN":

        pending = jobs.copy()

        while pending:

            available = [
                p for p in pending
                if p["arrival"] <= current_time
            ]

            if not available:
                next_arrival = min(p["arrival"] for p in pending)

                gantt.append({
                    "process": "Idle",
                    "start": current_time,
                    "end": next_arrival
                })

                current_time = next_arrival
                continue

            if algorithm == "FCFS":
                selected = min(
                    available,
                    key=lambda p: (p["arrival"], jobs.index(p))
                )

            elif algorithm == "SJF":
                selected = min(
                    available,
                    key=lambda p: (p["burst"], p["arrival"])
                )

            else:
                selected = min(
                    available,
                    key=lambda p: (p["priority"], p["arrival"])
                )

            start = current_time
            current_time += selected["burst"]

            pid = selected["pid"]

            gantt.append({
                "process": pid,
                "start": start,
                "end": current_time
            })

            completed[pid] = {
                "completion_time": current_time,
                "response_time": start - selected["arrival"]
            }

            pending.remove(selected)

    # ---------- ROUND ROBIN ----------

    else:

        ready = deque()
        pending = sorted(jobs, key=lambda p: p["arrival"])
        current_time = 0

        while pending or ready:

            if not ready:

                next_arrival = pending[0]["arrival"]

                if current_time < next_arrival:
                    gantt.append({
                        "process": "Idle",
                        "start": current_time,
                        "end": next_arrival
                    })

                    current_time = next_arrival

            while pending and pending[0]["arrival"] <= current_time:
                ready.append(pending.pop(0))

            process = ready.popleft()
            pid = process["pid"]

            start = current_time

            execute = min(quantum, remaining[pid])
            current_time += execute
            remaining[pid] -= execute

            gantt.append({
                "process": pid,
                "start": start,
                "end": current_time
            })

            while pending and pending[0]["arrival"] <= current_time:
                ready.append(pending.pop(0))

            if remaining[pid] > 0:
                ready.append(process)
            else:
                completed[pid] = {
                    "completion_time": current_time
                }

    # ---------- PERFORMANCE METRICS ----------

    results = []

    for p in jobs:

        pid = p["pid"]
        completion = completed[pid]["completion_time"]

        turnaround = completion - p["arrival"]
        waiting = turnaround - p["burst"]

        response = completed[pid].get(
            "response_time",
            next(
                item["start"] - p["arrival"]
                for item in gantt
                if item["process"] == pid
            )
        )

        results.append({
            "pid": pid,
            "arrival_time": p["arrival"],
            "burst_time": p["burst"],
            "completion_time": completion,
            "turnaround_time": turnaround,
            "waiting_time": waiting,
            "response_time": response
        })

    total_waiting = sum(p["waiting_time"] for p in results)
    total_turnaround = sum(p["turnaround_time"] for p in results)

    total_burst = sum(p["burst"] for p in jobs)

    total_time = current_time

    cpu_utilization = (
        total_burst / total_time * 100
        if total_time else 0
    )

    return {
        "algorithm": algorithm,
        "gantt_chart": gantt,
        "processes": results,
        "average_waiting_time": round(
            total_waiting / len(results), 2
        ),
        "average_turnaround_time": round(
            total_turnaround / len(results), 2
        ),
        "cpu_utilization": round(cpu_utilization, 2)
    }


# =========================================================
# 2. MEMORY MANAGEMENT
# =========================================================

def memory_management(blocks, processes, algorithm="FIRST FIT"):

    if not blocks or not processes:
        raise ValueError("Blocks and processes cannot be empty.")

    blocks = [int(b) for b in blocks]
    processes = [int(p) for p in processes]

    if any(b <= 0 for b in blocks):
        raise ValueError("Block sizes must be positive.")

    if any(p <= 0 for p in processes):
        raise ValueError("Process sizes must be positive.")

    algorithm = algorithm.upper()

    if algorithm not in ["FIRST FIT", "BEST FIT", "WORST FIT"]:
        raise ValueError("Invalid memory allocation algorithm.")

    available = [True] * len(blocks)
    allocations = []

    for i, process_size in enumerate(processes):

        suitable = [
            j for j in range(len(blocks))
            if available[j] and blocks[j] >= process_size
        ]

        selected = None

        if suitable:

            if algorithm == "FIRST FIT":
                selected = suitable[0]

            elif algorithm == "BEST FIT":
                selected = min(
                    suitable,
                    key=lambda j: blocks[j]
                )

            elif algorithm == "WORST FIT":
                selected = max(
                    suitable,
                    key=lambda j: blocks[j]
                )

        if selected is not None:

            available[selected] = False

            allocations.append({
                "process_id": f"P{i + 1}",
                "process_size": process_size,
                "block_number": selected + 1,
                "block_size": blocks[selected],
                "internal_fragmentation": (
                    blocks[selected] - process_size
                ),
                "status": "Allocated"
            })

        else:

            allocations.append({
                "process_id": f"P{i + 1}",
                "process_size": process_size,
                "block_number": None,
                "block_size": None,
                "internal_fragmentation": 0,
                "status": "Not Allocated"
            })

    allocated = sum(
        1 for a in allocations
        if a["status"] == "Allocated"
    )

    fragmentation = sum(
        a["internal_fragmentation"]
        for a in allocations
    )

    return {
        "algorithm": algorithm,
        "allocations": allocations,
        "total_processes": len(processes),
        "allocated_processes": allocated,
        "unallocated_processes": len(processes) - allocated,
        "total_internal_fragmentation": fragmentation,
        "remaining_blocks": [
            blocks[i]
            for i in range(len(blocks))
            if available[i]
        ]
    }


# =========================================================
# 3. DEADLOCK AVOIDANCE - BANKER'S ALGORITHM
# =========================================================

def bankers_algorithm(allocation, maximum, available):

    if not allocation or not maximum:
        raise ValueError("Allocation and maximum matrices are required.")

    n = len(allocation)
    m = len(available)

    if len(maximum) != n:
        raise ValueError("Matrix row counts must match.")

    if any(len(row) != m for row in allocation + maximum):
        raise ValueError("Matrix column counts must match available.")

    allocation = [[int(x) for x in row] for row in allocation]
    maximum = [[int(x) for x in row] for row in maximum]
    available = [int(x) for x in available]

    if any(x < 0 for row in allocation + maximum for x in row):
        raise ValueError("Resource values cannot be negative.")

    if any(x < 0 for x in available):
        raise ValueError("Available resources cannot be negative.")

    for i in range(n):
        for j in range(m):
            if maximum[i][j] < allocation[i][j]:
                raise ValueError("Maximum cannot be less than allocation.")

    need = [
        [
            maximum[i][j] - allocation[i][j]
            for j in range(m)
        ]
        for i in range(n)
    ]

    work = available.copy()
    finish = [False] * n
    safe_sequence = []

    while len(safe_sequence) < n:

        found = False

        for i in range(n):

            if not finish[i]:

                can_execute = all(
                    need[i][j] <= work[j]
                    for j in range(m)
                )

                if can_execute:

                    for j in range(m):
                        work[j] += allocation[i][j]

                    finish[i] = True
                    safe_sequence.append(f"P{i}")

                    found = True

        if not found:
            break

    is_safe = all(finish)

    return {
        "is_safe": is_safe,
        "status": "SAFE STATE" if is_safe else "UNSAFE STATE",
        "safe_sequence": safe_sequence,
        "need_matrix": need,
        "available_resources": available
    }


# =========================================================
# 4. DISK SCHEDULING
# =========================================================

def disk_scheduling(
    requests,
    head,
    algorithm="FCFS",
    disk_size=200,
    direction="RIGHT"
):

    if disk_size <= 0:
        raise ValueError("Disk size must be positive.")

    requests = [int(r) for r in requests]
    head = int(head)

    if not 0 <= head < disk_size:
        raise ValueError("Head position is outside disk range.")

    if any(r < 0 or r >= disk_size for r in requests):
        raise ValueError("Invalid disk request position.")

    algorithm = algorithm.upper()
    direction = direction.upper()

    if algorithm not in ["FCFS", "SSTF", "SCAN", "C-SCAN"]:
        raise ValueError("Invalid disk scheduling algorithm.")

    if direction not in ["LEFT", "RIGHT"]:
        raise ValueError("Direction must be LEFT or RIGHT.")

    sequence = []
    pending = requests.copy()

    # ---------- FCFS ----------

    if algorithm == "FCFS":
        sequence = pending.copy()

    # ---------- SSTF ----------

    elif algorithm == "SSTF":

        current = head

        while pending:

            selected = min(
                pending,
                key=lambda r: abs(r - current)
            )

            sequence.append(selected)
            pending.remove(selected)
            current = selected

    # ---------- SCAN ----------

    elif algorithm == "SCAN":

        left = sorted(
            [r for r in pending if r < head],
            reverse=True
        )

        right = sorted(
            [r for r in pending if r >= head]
        )

        if direction == "RIGHT":

            sequence = right + [disk_size - 1] + left

        else:

            sequence = left + [0] + right

    # ---------- C-SCAN ----------

    elif algorithm == "C-SCAN":

        left = sorted(
            [r for r in pending if r < head]
        )

        right = sorted(
            [r for r in pending if r >= head]
        )

        if direction == "RIGHT":

            sequence = right + [disk_size - 1, 0] + left

        else:

            sequence = left[::-1] + [0, disk_size - 1] + right[::-1]

    # Remove unnecessary consecutive duplicate positions.
    clean_sequence = []

    for position in sequence:
        if not clean_sequence or position != clean_sequence[-1]:
            clean_sequence.append(position)

    total_movement = 0
    current = head

    for position in clean_sequence:

        total_movement += abs(position - current)
        current = position

    return {
        "algorithm": algorithm,
        "initial_head": head,
        "direction": direction,
        "seek_sequence": clean_sequence,
        "total_head_movement": total_movement,
        "average_seek_movement": round(
            total_movement / len(requests), 2
        ) if requests else 0
    }
