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


def simulate_fcfs(processes: List[Process]) -> None:
    current_time = 0
    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.waiting_time = current_time - p.arrival_time
        current_time += p.burst_time
        p.turnaround_time = p.waiting_time + p.burst_time
        p.completion_time = current_time


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
        self.title("CPU Scheduling Simulator (FCFS)")
        self.geometry("900x600")
        self.minsize(900, 600)

        self.processes: List[Process] = []

        self._build_ui()
        self._try_load_default()

    def _build_ui(self) -> None:
        header = tk.Label(self, text="CPU Scheduling Simulator (FCFS)", font=("Arial", 18, "bold"))
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
        tk.Button(action_box, text="Run FCFS", command=self.run_fcfs).grid(row=0, column=2, padx=5, pady=4)

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

    def run_fcfs(self) -> None:
        if not self.processes:
            messagebox.showwarning("No Data", "Load or add processes first.")
            return
        reset_stats(self.processes)
        simulate_fcfs(self.processes)

        # Build results
        total_wt = 0
        total_tat = 0
        lines = ["[FCFS Results]", "Process\tAT\tBT\tCT\tTAT\tWT"]
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


def main() -> None:
    app = SchedulerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
