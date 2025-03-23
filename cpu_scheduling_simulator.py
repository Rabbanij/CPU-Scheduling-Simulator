import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np

# Function to calculate waiting time and turnaround time for FCFS
def fcfs(processes):
    processes.sort(key=lambda x: x[3])  # Sort by arrival time
    n = len(processes)
    waiting_time = [0] * n
    turnaround_time = [0] * n
    current_time = 0

    for i in range(n):
        _, burst_time, _, arrival_time = processes[i]
        if current_time < arrival_time:
            current_time = arrival_time  # Handle idle time
        waiting_time[i] = current_time - arrival_time
        current_time += burst_time
        turnaround_time[i] = waiting_time[i] + burst_time

    return waiting_time, turnaround_time

# Function to calculate waiting time and turnaround time for SJF
def sjf(processes):
    processes.sort(key=lambda x: x[3])  # Sort by arrival time
    n = len(processes)
    waiting_time = [0] * n
    turnaround_time = [0] * n

    completed = [False] * n
    current_time = 0
    completed_count = 0

    while completed_count < n:
        available_processes = [i for i in range(n) if not completed[i] and processes[i][3] <= current_time]
        if not available_processes:
            current_time += 1  # Idle time
            continue

        shortest_job = min(available_processes, key=lambda i: processes[i][1])
        _, burst_time, _, arrival_time = processes[shortest_job]
        waiting_time[shortest_job] = current_time - arrival_time
        current_time += burst_time
        turnaround_time[shortest_job] = waiting_time[shortest_job] + burst_time
        completed[shortest_job] = True
        completed_count += 1

    return waiting_time, turnaround_time

# Function to calculate waiting time and turnaround time for Round Robin
def round_robin(processes, quantum):
    n = len(processes)
    waiting_time = [0] * n
    remaining_burst_time = [p[1] for p in processes]
    arrival_time = [p[3] for p in processes]
    time = 0
    completed = 0
    total_burst_time = sum(remaining_burst_time)

    while completed < n:
        idle = True
        for i in range(n):
            if remaining_burst_time[i] > 0 and arrival_time[i] <= time:
                idle = False
                if remaining_burst_time[i] <= quantum:
                    time += remaining_burst_time[i]
                    waiting_time[i] = time - processes[i][1] - arrival_time[i]
                    remaining_burst_time[i] = 0
                    completed += 1
                else:
                    time += quantum
                    remaining_burst_time[i] -= quantum

        if idle:
            time += 1  # Increment time if CPU is idle

    turnaround_time = [waiting_time[i] + processes[i][1] for i in range(n)]
    return waiting_time, turnaround_time

# Function to calculate waiting time and turnaround time for Priority Scheduling
def priority_scheduling(processes):
    processes.sort(key=lambda x: (x[3], -x[2]))  # Sort by arrival time and priority
    return fcfs(processes)

# Function to calculate performance metrics
def calculate_metrics(waiting_time, turnaround_time, processes):
    avg_waiting_time = np.mean(waiting_time)
    avg_turnaround_time = np.mean(turnaround_time)
    total_burst_time = sum([p[1] for p in processes])
    max_time = max(turnaround_time[i] + processes[i][3] for i in range(len(processes)))
    cpu_utilization = (total_burst_time / max_time) * 100
    throughput = len(processes) / max_time
    return avg_waiting_time, avg_turnaround_time, cpu_utilization, throughput

# Function to draw the Gantt chart
def draw_gantt_chart(processes, waiting_time, turnaround_time, algorithm):
    plt.figure(figsize=(10, 6))
    start_times = [0] * len(processes)
    end_times = [0] * len(processes)
    current_time = 0

    for i in range(len(processes)):
        _, burst_time, _, arrival_time = processes[i]
        if current_time < arrival_time:
            current_time = arrival_time  # Handle idle time
        start_times[i] = current_time
        current_time += burst_time
        end_times[i] = current_time

    for i in range(len(processes)):
        plt.barh(0, end_times[i] - start_times[i], left=start_times[i], color="skyblue", edgecolor="black")
        plt.text((start_times[i] + end_times[i]) / 2, 0, processes[i][0], ha='center', va='center', color='black')

    plt.yticks([])
    plt.xlabel("Time")
    plt.title(f"Gantt Chart - {algorithm}")
    plt.grid(axis='x')
    plt.show()

# Function to handle the simulation
def simulate():
    try:
        processes = []
        num_processes = int(entry_num_processes.get())
        for i in range(num_processes):
            arrival_time = int(entries_arrival_time[i].get())
            burst_time = int(entries_burst_time[i].get())
            priority = int(entries_priority[i].get())
            processes.append((f"P{i+1}", burst_time, priority, arrival_time))
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values.")
        return

    selected_algorithm = combo_algorithm.get()
    if selected_algorithm == "FCFS":
        waiting_time, turnaround_time = fcfs(processes)
    elif selected_algorithm == "SJF":
        waiting_time, turnaround_time = sjf(processes)
    elif selected_algorithm == "Round Robin":
        try:
            quantum = int(entry_quantum.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid quantum value.")
            return
        waiting_time, turnaround_time = round_robin(processes, quantum)
    elif selected_algorithm == "Priority Scheduling":
        waiting_time, turnaround_time = priority_scheduling(processes)
    else:
        messagebox.showerror("Input Error", "Please select an algorithm.")
        return

    avg_waiting_time, avg_turnaround_time, cpu_utilization, throughput = calculate_metrics(waiting_time, turnaround_time, processes)
    messagebox.showinfo("Results", f"Average Waiting Time: {avg_waiting_time:.2f}\n"
                                    f"Average Turnaround Time: {avg_turnaround_time:.2f}\n"
                                    f"CPU Utilization: {cpu_utilization:.2f}%\n"
                                    f"Throughput: {throughput:.2f} processes/unit time")

    draw_gantt_chart(processes, waiting_time, turnaround_time, selected_algorithm)

# Set up the GUI
root = tk.Tk()
root.title("CPU Scheduling Simulator")

label_num_processes = tk.Label(root, text="Enter the number of processes:")
label_num_processes.grid(row=0, column=0)
entry_num_processes = tk.Entry(root)
entry_num_processes.grid(row=0, column=1)

label_processes = tk.Label(root, text="Enter process details (arrival time, burst time, priority):")
label_processes.grid(row=1, column=0, columnspan=2)

entries_arrival_time = []
entries_burst_time = []
entries_priority = []
def create_process_inputs():
    try:
        num_processes = int(entry_num_processes.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of processes.")
        return
    for widget in frame_process_inputs.winfo_children():
        widget.destroy()
    global entries_arrival_time, entries_burst_time, entries_priority
    entries_arrival_time = []
    entries_burst_time = []
    entries_priority = []
    for i in range(num_processes):
        label_process = tk.Label(frame_process_inputs, text=f"Process {i+1}:")
        label_process.grid(row=i, column=0)
        entry_arrival_time = tk.Entry(frame_process_inputs)
        entry_arrival_time.grid(row=i, column=1)
        entries_arrival_time.append(entry_arrival_time)
        entry_burst_time = tk.Entry(frame_process_inputs)
        entry_burst_time.grid(row=i, column=2)
        entries_burst_time.append(entry_burst_time)
        entry_priority = tk.Entry(frame_process_inputs)
        entry_priority.grid(row=i, column=3)
        entries_priority.append(entry_priority)

frame_process_inputs = tk.Frame(root)
frame_process_inputs.grid(row=2, column=0, columnspan=2)
create_process_inputs_button = tk.Button(root, text="Create Process Inputs", command=create_process_inputs)
create_process_inputs_button.grid(row=1, column=2)

label_algorithm = tk.Label(root, text="Select Scheduling Algorithm:")
label_algorithm.grid(row=3, column=0)
combo_algorithm = tk.StringVar(root)
combo_algorithm.set("FCFS")
dropdown_algorithm = tk.OptionMenu(root, combo_algorithm, "FCFS", "SJF", "Round Robin", "Priority Scheduling")
dropdown_algorithm.grid(row=3, column=1)

label_quantum = tk.Label(root, text="Enter Time Quantum (for Round Robin):")
label_quantum.grid(row=4, column=0)
entry_quantum = tk.Entry(root)
entry_quantum.grid(row=4, column=1)

button_run = tk.Button(root, text="Run Simulation", command=simulate)
button_run.grid(row=5, column=0, columnspan=2)

root.mainloop()
