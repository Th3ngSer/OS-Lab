#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import tkinter as tk
from tkinter import filedialog, messagebox


@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    remaining_time: int = 0
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0


def reset_stats(processes: List[Process]) -> None:
    for p in processes:
        p.remaining_time = p.burst_time
        p.completion_time = 0
        p.turnaround_time = 0
        p.waiting_time = 0


def _add_segment(segments: List[tuple], pid: int, start: int, end: int) -> None:
    if start == end:
        return
    if segments and segments[-1][0] == pid and segments[-1][2] == start:
        segments[-1] = (pid, segments[-1][1], end)
        return
    segments.append((pid, start, end))


def load_processes_from_file(path: str) -> List[Process]:
    processes: List[Process] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                pid, at, bt = map(int, parts[:3])
                if at < 0 or bt <= 0:
                    continue
                processes.append(Process(pid, at, bt, bt))
    except FileNotFoundError:
        return []

    return processes


def enter_processes_manually() -> List[Process]:
    while True:
        try:
            n = int(input("Enter number of processes: "))
            if n <= 0:
                print("Invalid number. Try again.")
                continue
            break
        except ValueError:
            print("Invalid number. Try again.")

    processes: List[Process] = []
    for i in range(n):
        while True:
            try:
                pid = int(input(f"Process {i + 1} ID: "))
                break
            except ValueError:
                print("Invalid ID. Try again.")
        while True:
            try:
                at = int(input("Arrival Time: "))
                if at < 0:
                    print("Invalid Arrival Time. Try again.")
                    continue
                break
            except ValueError:
                print("Invalid Arrival Time. Try again.")
        while True:
            try:
                bt = int(input("Burst Time: "))
                if bt <= 0:
                    print("Invalid Burst Time. Try again.")
                    continue
                break
            except ValueError:
                print("Invalid Burst Time. Try again.")
        processes.append(Process(pid, at, bt, bt))

    return processes


def simulate_fcfs(processes: List[Process]) -> List[tuple]:
    segments: List[tuple] = []
    current_time = 0
    for p in processes:
        if current_time < p.arrival_time:
            _add_segment(segments, -1, current_time, p.arrival_time)
            current_time = p.arrival_time
        _add_segment(segments, p.pid, current_time, current_time + p.burst_time)
        p.waiting_time = current_time - p.arrival_time
        current_time += p.burst_time
        p.turnaround_time = p.waiting_time + p.burst_time
        p.completion_time = current_time
    return segments


def simulate_sjf(processes: List[Process]) -> List[tuple]:
    n = len(processes)
    completed = 0
    current_time = 0
    done = [False] * n
    segments: List[tuple] = []

    while completed < n:
        idx = -1
        min_bt = 10**9
        for i, p in enumerate(processes):
            if not done[i] and p.arrival_time <= current_time and p.burst_time < min_bt:
                min_bt = p.burst_time
                idx = i

        if idx == -1:
            _add_segment(segments, -1, current_time, current_time + 1)
            current_time += 1
            continue

        p = processes[idx]
        _add_segment(segments, p.pid, current_time, current_time + p.burst_time)
        p.waiting_time = current_time - p.arrival_time
        current_time += p.burst_time
        p.completion_time = current_time
        p.turnaround_time = p.completion_time - p.arrival_time
        done[idx] = True
        completed += 1
    return segments


def simulate_srtf(processes: List[Process]) -> List[tuple]:
    n = len(processes)
    completed = 0
    current_time = 0
    segments: List[tuple] = []

    while completed < n:
        idx = -1
        min_remaining = 10**9
        for i, p in enumerate(processes):
            if p.arrival_time <= current_time and p.remaining_time > 0:
                if p.remaining_time < min_remaining:
                    min_remaining = p.remaining_time
                    idx = i

        if idx == -1:
            _add_segment(segments, -1, current_time, current_time + 1)
            current_time += 1
            continue

        _add_segment(segments, processes[idx].pid, current_time, current_time + 1)
        processes[idx].remaining_time -= 1
        current_time += 1

        if processes[idx].remaining_time == 0:
            completed += 1
            p = processes[idx]
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
    return segments


def simulate_rr(processes: List[Process], quantum: int) -> List[tuple]:
    n = len(processes)
    rem = [p.burst_time for p in processes]
    current_time = 0
    completed = 0
    i = 0
    segments: List[tuple] = []

    # processes assumed sorted by arrival time
    queue: List[int] = []
    while i < n and processes[i].arrival_time <= current_time:
        queue.append(i)
        i += 1

    while completed < n:
        if not queue:
            next_time = max(current_time, processes[i].arrival_time)
            _add_segment(segments, -1, current_time, next_time)
            current_time = next_time
            while i < n and processes[i].arrival_time <= current_time:
                queue.append(i)
                i += 1
            continue

        idx = queue.pop(0)
        run = min(quantum, rem[idx])
        _add_segment(segments, processes[idx].pid, current_time, current_time + run)
        rem[idx] -= run
        current_time += run

        while i < n and processes[i].arrival_time <= current_time:
            queue.append(i)
            i += 1

        if rem[idx] > 0:
            queue.append(idx)
        else:
            completed += 1
            p = processes[idx]
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
    return segments


def simulate_mlfq(processes: List[Process], q1: int = 2, q2: int = 4) -> List[tuple]:
    n = len(processes)
    remaining = [p.burst_time for p in processes]
    current_time = 0
    completed = 0
    i = 0
    segments: List[tuple] = []

    q1_queue: List[int] = []
    q2_queue: List[int] = []
    q3_queue: List[int] = []

    def add_arrivals() -> None:
        nonlocal i
        while i < n and processes[i].arrival_time <= current_time:
            q1_queue.append(i)
            i += 1

    add_arrivals()

    while completed < n:
        if not (q1_queue or q2_queue or q3_queue):
            next_time = max(current_time, processes[i].arrival_time)
            _add_segment(segments, -1, current_time, next_time)
            current_time = next_time
            add_arrivals()
            continue

        if q1_queue:
            idx = q1_queue.pop(0)
            run = min(q1, remaining[idx])
            _add_segment(segments, processes[idx].pid, current_time, current_time + run)
            remaining[idx] -= run
            current_time += run
            add_arrivals()
            if remaining[idx] > 0:
                q2_queue.append(idx)
            else:
                completed += 1
                p = processes[idx]
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
            continue

        if q2_queue:
            idx = q2_queue.pop(0)
            run = min(q2, remaining[idx])
            _add_segment(segments, processes[idx].pid, current_time, current_time + run)
            remaining[idx] -= run
            current_time += run
            add_arrivals()
            if remaining[idx] > 0:
                q3_queue.append(idx)
            else:
                completed += 1
                p = processes[idx]
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
            continue

        if q3_queue:
            idx = q3_queue.pop(0)
            run = remaining[idx]
            _add_segment(segments, processes[idx].pid, current_time, current_time + run)
            remaining[idx] = 0
            current_time += run
            add_arrivals()
            completed += 1
            p = processes[idx]
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
    return segments


def print_processes(processes: List[Process]) -> None:
    if not processes:
        print("No processes loaded.")
        return
    print("ID\tAT\tBT")
    for p in processes:
        print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}")


def print_results(processes: List[Process]) -> None:
    if not processes:
        print("No processes to display.")
        return
    total_wt = 0
    total_tat = 0
    print("Process\tAT\tBT\tCT\tTAT\tWT")
    for p in processes:
        total_wt += p.waiting_time
        total_tat += p.turnaround_time
        print(
            f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t"
            f"{p.completion_time}\t{p.turnaround_time}\t{p.waiting_time}"
        )
    avg_wt = total_wt / len(processes)
    avg_tat = total_tat / len(processes)
    print(f"\nAverage Waiting Time: {avg_wt:.2f}")
    print(f"Average Turnaround Time: {avg_tat:.2f}")


class SchedulerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CPU Scheduling Simulator")
        self.geometry("900x600")
        self.minsize(900, 600)

        self.processes: List[Process] = []

        self._build_ui()
        self._try_load_default()

    def _build_ui(self) -> None:
        header = tk.Label(self, text="CPU Scheduling Simulator", font=("Arial", 18, "bold"))
        header.pack(pady=10)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        left = tk.Frame(container)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right = tk.Frame(container)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Input section
        input_box = tk.LabelFrame(left, text="Add Process", padx=8, pady=8)
        input_box.pack(fill=tk.X)

        tk.Label(input_box, text="ID").grid(row=0, column=0, sticky="w")
        tk.Label(input_box, text="Arrival Time").grid(row=0, column=1, sticky="w")
        tk.Label(input_box, text="Burst Time").grid(row=0, column=2, sticky="w")

        self.id_entry = tk.Entry(input_box, width=10)
        self.at_entry = tk.Entry(input_box, width=12)
        self.bt_entry = tk.Entry(input_box, width=12)
        self.id_entry.grid(row=1, column=0, padx=5, pady=4)
        self.at_entry.grid(row=1, column=1, padx=5, pady=4)
        self.bt_entry.grid(row=1, column=2, padx=5, pady=4)

        add_btn = tk.Button(input_box, text="Add", command=self.add_process)
        add_btn.grid(row=1, column=3, padx=6)

        # Actions
        action_box = tk.LabelFrame(left, text="Actions", padx=8, pady=8)
        action_box.pack(fill=tk.X, pady=10)

        tk.Button(action_box, text="Load From File", command=self.load_from_file).grid(row=0, column=0, padx=5, pady=4)
        tk.Button(action_box, text="Clear All", command=self.clear_processes).grid(row=0, column=1, padx=5, pady=4)
        tk.Button(action_box, text="Run Selected", command=self.run_selected).grid(row=0, column=2, padx=5, pady=4)

        # Algorithm controls
        algo_box = tk.LabelFrame(left, text="Algorithm", padx=8, pady=8)
        algo_box.pack(fill=tk.X, pady=6)

        self.algorithm_var = tk.StringVar(value="FCFS")
        algo_options = ["FCFS", "SJF", "SRTF", "RR", "MLFQ"]
        self.algorithm_menu = tk.OptionMenu(algo_box, self.algorithm_var, *algo_options)
        self.algorithm_menu.grid(row=0, column=0, padx=5, pady=4, sticky="w")

        tk.Label(algo_box, text="RR Quantum").grid(row=0, column=1, padx=5, sticky="e")
        self.rr_quantum_entry = tk.Entry(algo_box, width=6)
        self.rr_quantum_entry.insert(0, "2")
        self.rr_quantum_entry.grid(row=0, column=2, padx=5)

        tk.Label(algo_box, text="MLFQ Q1").grid(row=1, column=1, padx=5, sticky="e")
        self.mlfq_q1_entry = tk.Entry(algo_box, width=6)
        self.mlfq_q1_entry.insert(0, "2")
        self.mlfq_q1_entry.grid(row=1, column=2, padx=5)

        tk.Label(algo_box, text="MLFQ Q2").grid(row=1, column=3, padx=5, sticky="e")
        self.mlfq_q2_entry = tk.Entry(algo_box, width=6)
        self.mlfq_q2_entry.insert(0, "4")
        self.mlfq_q2_entry.grid(row=1, column=4, padx=5)

        # Process list
        list_box = tk.LabelFrame(left, text="Current Processes", padx=8, pady=8)
        list_box.pack(fill=tk.BOTH, expand=True)

        self.process_list = tk.Text(list_box, height=10, wrap="none")
        self.process_list.pack(fill=tk.BOTH, expand=True)

        # Results
        results_box = tk.LabelFrame(right, text="Results", padx=8, pady=8)
        results_box.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(results_box, height=20, wrap="none")
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Gantt Chart
        gantt_box = tk.LabelFrame(right, text="Gantt Chart", padx=8, pady=8)
        gantt_box.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self.gantt_canvas = tk.Canvas(gantt_box, height=120, bg="white")
        self.gantt_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.gantt_scroll = tk.Scrollbar(gantt_box, orient=tk.HORIZONTAL, command=self.gantt_canvas.xview)
        self.gantt_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.gantt_canvas.configure(xscrollcommand=self.gantt_scroll.set)

        footer = tk.Label(self, text="Input format: ID ArrivalTime BurstTime", fg="#666")
        footer.pack(pady=6)

    def _try_load_default(self) -> None:
        default_file = "processes.txt"
        loaded = load_processes_from_file(default_file)
        if loaded:
            self.processes = loaded
            self._refresh_process_list()

    def _refresh_process_list(self) -> None:
        self.process_list.delete("1.0", tk.END)
        if not self.processes:
            self.process_list.insert(tk.END, "No processes loaded.\n")
            return
        self.process_list.insert(tk.END, "ID\tAT\tBT\n")
        for p in self.processes:
            self.process_list.insert(tk.END, f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\n")

    def _set_results(self, text: str) -> None:
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, text)

    def _draw_gantt(self, segments: List[tuple]) -> None:
        self.gantt_canvas.delete("all")
        if not segments:
            return

        scale = 25
        y = 20
        height = 40
        max_time = max(seg[2] for seg in segments)

        for pid, start, end in segments:
            x1 = start * scale + 10
            x2 = end * scale + 10
            color = "#c7e8ff" if pid != -1 else "#e8e8e8"
            label = f"P{pid}" if pid != -1 else "IDLE"
            self.gantt_canvas.create_rectangle(x1, y, x2, y + height, fill=color, outline="#333")
            self.gantt_canvas.create_text((x1 + x2) / 2, y + height / 2, text=label, font=("Arial", 10, "bold"))
            self.gantt_canvas.create_text(x1, y + height + 12, text=str(start), anchor="n", font=("Arial", 9))

        self.gantt_canvas.create_text(max_time * scale + 10, y + height + 12, text=str(max_time), anchor="n", font=("Arial", 9))
        self.gantt_canvas.configure(scrollregion=(0, 0, max_time * scale + 40, y + height + 30))

    def add_process(self) -> None:
        try:
            pid = int(self.id_entry.get().strip())
            at = int(self.at_entry.get().strip())
            bt = int(self.bt_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integer values.")
            return

        if at < 0 or bt <= 0:
            messagebox.showerror("Invalid Input", "Arrival time must be >= 0 and burst time > 0.")
            return

        self.processes.append(Process(pid, at, bt, bt))
        self._refresh_process_list()
        self.id_entry.delete(0, tk.END)
        self.at_entry.delete(0, tk.END)
        self.bt_entry.delete(0, tk.END)

    def load_from_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select processes file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*")],
        )
        if not file_path:
            return
        loaded = load_processes_from_file(file_path)
        if loaded:
            self.processes = loaded
            self._refresh_process_list()
        else:
            messagebox.showerror("Load Failed", "File is empty or invalid format.")

    def clear_processes(self) -> None:
        self.processes = []
        self._refresh_process_list()
        self._set_results("")

    def _build_results(self, title: str) -> None:
        total_wt = 0
        total_tat = 0
        lines = [f"[{title} Results]", "Process\tAT\tBT\tCT\tTAT\tWT"]
        for p in self.processes:
            total_wt += p.waiting_time
            total_tat += p.turnaround_time
            lines.append(
                f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t"
                f"{p.completion_time}\t{p.turnaround_time}\t{p.waiting_time}"
            )
        avg_wt = total_wt / len(self.processes)
        avg_tat = total_tat / len(self.processes)
        lines.append("")
        lines.append(f"Average Waiting Time: {avg_wt:.2f}")
        lines.append(f"Average Turnaround Time: {avg_tat:.2f}")
        self._set_results("\n".join(lines))

    def run_selected(self) -> None:
        if not self.processes:
            messagebox.showwarning("No Data", "Load or add processes first.")
            return

        # Ensure stable order by arrival time for preemptive algorithms
        self.processes.sort(key=lambda p: (p.arrival_time, p.pid))
        reset_stats(self.processes)

        algo = self.algorithm_var.get()
        if algo == "FCFS":
            segments = simulate_fcfs(self.processes)
            self._build_results("FCFS")
            self._draw_gantt(segments)
            return
        if algo == "SJF":
            segments = simulate_sjf(self.processes)
            self._build_results("SJF")
            self._draw_gantt(segments)
            return
        if algo == "SRTF":
            segments = simulate_srtf(self.processes)
            self._build_results("SRTF")
            self._draw_gantt(segments)
            return
        if algo == "RR":
            try:
                quantum = int(self.rr_quantum_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Quantum", "RR quantum must be an integer.")
                return
            if quantum <= 0:
                messagebox.showerror("Invalid Quantum", "RR quantum must be > 0.")
                return
            segments = simulate_rr(self.processes, quantum)
            self._build_results(f"RR (Q={quantum})")
            self._draw_gantt(segments)
            return
        if algo == "MLFQ":
            try:
                q1 = int(self.mlfq_q1_entry.get().strip())
                q2 = int(self.mlfq_q2_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Quantum", "MLFQ Q1/Q2 must be integers.")
                return
            if q1 <= 0 or q2 <= 0:
                messagebox.showerror("Invalid Quantum", "MLFQ Q1/Q2 must be > 0.")
                return
            segments = simulate_mlfq(self.processes, q1=q1, q2=q2)
            self._build_results(f"MLFQ (Q1={q1}, Q2={q2})")
            self._draw_gantt(segments)
            return


def main() -> None:
    app = SchedulerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
