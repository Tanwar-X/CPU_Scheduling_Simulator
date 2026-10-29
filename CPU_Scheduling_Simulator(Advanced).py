
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from collections import deque

# ============================================================
# CPU SCHEDULING SIMULATOR - PYTHON 3.14
# FCFS | SJF | ROUND ROBIN | PRIORITY
# ============================================================

BG = "#F1F5F9"
PANEL = "#FFFFFF"
NAVY = "#172554"
BLUE = "#2563EB"
TEAL = "#0F766E"
PURPLE = "#7C3AED"
ORANGE = "#EA580C"
GREEN = "#15803D"
RED = "#DC2626"
TEXT = "#1E293B"
MUTED = "#64748B"
BORDER = "#CBD5E1"

ALGORITHMS = ["FCFS", "SJF", "Round Robin", "Priority"]


# ============================================================
# SCHEDULING ALGORITHMS
# ============================================================

def fcfs(processes):
    ordered = sorted(processes, key=lambda p: (p["arrival"], p["order"]))
    time = 0
    segments = []

    for p in ordered:
        if time < p["arrival"]:
            segments.append({
                "pid": "IDLE", "start": time, "end": p["arrival"]
            })
            time = p["arrival"]

        start = time
        time += p["burst"]
        segments.append({
            "pid": p["pid"], "start": start, "end": time
        })

    return segments


def sjf(processes):
    remaining = processes[:]
    time = 0
    segments = []

    while remaining:
        available = [p for p in remaining if p["arrival"] <= time]

        if not available:
            next_time = min(p["arrival"] for p in remaining)
            if time < next_time:
                segments.append({
                    "pid": "IDLE", "start": time, "end": next_time
                })
            time = next_time
            continue

        p = min(
            available,
            key=lambda x: (x["burst"], x["arrival"], x["order"])
        )
        remaining.remove(p)

        start = time
        time += p["burst"]
        segments.append({
            "pid": p["pid"], "start": start, "end": time
        })

    return segments


def priority_scheduling(processes):
    remaining = processes[:]
    time = 0
    segments = []

    while remaining:
        available = [p for p in remaining if p["arrival"] <= time]

        if not available:
            next_time = min(p["arrival"] for p in remaining)
            if time < next_time:
                segments.append({
                    "pid": "IDLE", "start": time, "end": next_time
                })
            time = next_time
            continue

        p = min(
            available,
            key=lambda x: (x["priority"], x["arrival"], x["order"])
        )
        remaining.remove(p)

        start = time
        time += p["burst"]
        segments.append({
            "pid": p["pid"], "start": start, "end": time
        })

    return segments


def round_robin(processes, quantum):
    ordered = sorted(processes, key=lambda p: (p["arrival"], p["order"]))
    remaining = {p["pid"]: p["burst"] for p in ordered}
    ready = deque()
    segments = []
    index = 0
    time = 0

    while index < len(ordered) or ready:
        if not ready:
            if index < len(ordered) and time < ordered[index]["arrival"]:
                segments.append({
                    "pid": "IDLE",
                    "start": time,
                    "end": ordered[index]["arrival"]
                })
                time = ordered[index]["arrival"]

            while index < len(ordered) and ordered[index]["arrival"] <= time:
                ready.append(ordered[index])
                index += 1

            if not ready:
                continue

        p = ready.popleft()
        start = time
        duration = min(quantum, remaining[p["pid"]])
        time += duration
        remaining[p["pid"]] -= duration

        segments.append({
            "pid": p["pid"], "start": start, "end": time
        })

        while index < len(ordered) and ordered[index]["arrival"] <= time:
            ready.append(ordered[index])
            index += 1

        if remaining[p["pid"]] > 0:
            ready.append(p)

    return segments


def calculate_results(processes, segments):
    results = {}

    for p in processes:
        results[p["pid"]] = {
            **p,
            "completion": 0,
            "turnaround": 0,
            "waiting": 0,
            "response": None
        }

    for seg in segments:
        if seg["pid"] == "IDLE":
            continue

        row = results[seg["pid"]]
        if row["response"] is None:
            row["response"] = seg["start"] - row["arrival"]

        row["completion"] = max(row["completion"], seg["end"])

    for row in results.values():
        row["turnaround"] = row["completion"] - row["arrival"]
        row["waiting"] = row["turnaround"] - row["burst"]

        if row["response"] is None:
            row["response"] = 0

    return list(results.values())


# ============================================================
# GUI
# ============================================================

class CPUSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1250x850")
        self.root.minsize(950, 650)
        self.root.configure(bg=BG)

        self.processes = []
        self.results = {}
        self.segments = {}
        self.order_counter = 0

        self.setup_style()
        self.build_interface()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground=TEXT,
            fieldbackground="white",
            rowheight=28,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=NAVY,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=7
        )
        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", NAVY)]
        )
        style.configure(
            "TNotebook.Tab",
            padding=(15, 9),
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BLUE)],
            foreground=[("selected", "white")]
        )

    def button(self, parent, text, command, color=BLUE):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=NAVY,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=7
        )

    def panel(self, parent, title, color=BLUE):
        frame = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        heading = tk.Frame(frame, bg=color, height=36)
        heading.pack(fill="x")
        heading.pack_propagate(False)

        tk.Label(
            heading,
            text=title,
            bg=color,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=12
        ).pack(fill="both", expand=True)

        return frame

    def build_interface(self):
        header = tk.Frame(self.root, bg=NAVY, height=85)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="CPU SCHEDULING SIMULATOR",
            bg=NAVY,
            fg="white",
            font=("Segoe UI", 21, "bold")
        ).pack(pady=(12, 2))

        tk.Label(
            header,
            text="Operating System Scheduling Visualisation",
            bg=NAVY,
            fg="#BFDBFE",
            font=("Segoe UI", 10)
        ).pack()

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_tab = tk.Frame(self.tabs, bg=BG)
        self.results_tab = tk.Frame(self.tabs, bg=BG)
        self.compare_tab = tk.Frame(self.tabs, bg=BG)
        self.help_tab = tk.Frame(self.tabs, bg=BG)

        self.tabs.add(self.setup_tab, text="Process Setup")
        self.tabs.add(self.results_tab, text="Results & Gantt Chart")
        self.tabs.add(self.compare_tab, text="Comparison")
        self.tabs.add(self.help_tab, text="Help & Formulas")

        self.build_setup()
        self.build_results()
        self.build_comparison()
        self.build_help()

        footer = tk.Frame(self.root, bg="#E2E8F0")
        footer.pack(fill="x", side="bottom")
        tk.Label(
            footer,
            text="FCFS  |  SJF  |  Round Robin  |  Priority",
            bg="#E2E8F0",
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(pady=4)

    # --------------------------------------------------------
    # SETUP TAB
    # --------------------------------------------------------

    def build_setup(self):
        outer = tk.Frame(self.setup_tab, bg=BG)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        form = self.panel(outer, "ADD PROCESS", BLUE)
        form.pack(fill="x", pady=(0, 10))

        fields = tk.Frame(form, bg=PANEL)
        fields.pack(fill="x", padx=10, pady=10)

        self.pid_var = tk.StringVar()
        self.arrival_var = tk.StringVar(value="0")
        self.burst_var = tk.StringVar(value="5")
        self.priority_var = tk.StringVar(value="1")
        self.quantum_var = tk.StringVar(value="2")

        entries = [
            ("Process ID", self.pid_var),
            ("Arrival Time", self.arrival_var),
            ("Burst Time", self.burst_var),
            ("Priority", self.priority_var),
            ("RR Quantum", self.quantum_var)
        ]

        for i, (label, var) in enumerate(entries):
            cell = tk.Frame(fields, bg=PANEL)
            cell.grid(row=0, column=i, padx=6, sticky="ew")
            tk.Label(
                cell, text=label, bg=PANEL, fg=TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")
            ttk.Entry(cell, textvariable=var).pack(fill="x", pady=4)
            fields.grid_columnconfigure(i, weight=1)

        actions = tk.Frame(form, bg=PANEL)
        actions.pack(fill="x", padx=10, pady=(0, 10))

        self.button(
            actions, "Add Process", self.add_process, BLUE
        ).pack(side="left", padx=3)

        self.button(
            actions, "Remove Selected", self.remove_selected, RED
        ).pack(side="left", padx=3)

        self.button(
            actions, "Load Example", self.load_example, PURPLE
        ).pack(side="left", padx=3)

        self.button(
            actions, "Clear All", self.clear_all, MUTED
        ).pack(side="left", padx=3)

        self.button(
            actions, "Run All Algorithms", self.run_all, GREEN
        ).pack(side="right", padx=3)

        table_panel = self.panel(outer, "PROCESS TABLE", TEAL)
        table_panel.pack(fill="both", expand=True)

        body = tk.Frame(table_panel, bg=PANEL)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("pid", "arrival", "burst", "priority")
        self.process_table = ttk.Treeview(
            body, columns=cols, show="headings", height=9,
            selectmode="extended"
        )

        headings = {
            "pid": "Process ID",
            "arrival": "Arrival Time",
            "burst": "Burst Time",
            "priority": "Priority"
        }

        for col in cols:
            self.process_table.heading(col, text=headings[col])
            self.process_table.column(
                col, width=150, minwidth=90, anchor="center",
                stretch=True
            )

        sy = ttk.Scrollbar(
            body, orient="vertical", command=self.process_table.yview
        )
        self.process_table.configure(yscrollcommand=sy.set)
        self.process_table.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

        tk.Label(
            outer,
            text="Smaller priority number = higher priority. "
                 "Times use logical simulation units.",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=6)

    def add_process(self):
        pid = self.pid_var.get().strip() or f"P{len(self.processes) + 1}"

        if any(p["pid"] == pid for p in self.processes):
            messagebox.showerror("Error", "Process ID must be unique.")
            return

        try:
            arrival = int(self.arrival_var.get())
            burst = int(self.burst_var.get())
            priority = int(self.priority_var.get())
            quantum = int(self.quantum_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Enter valid integer values."
            )
            return

        if arrival < 0 or burst <= 0 or priority < 0 or quantum <= 0:
            messagebox.showerror(
                "Invalid Input",
                "Arrival and priority must be non-negative. "
                "Burst and quantum must be positive."
            )
            return

        self.order_counter += 1
        p = {
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "priority": priority,
            "order": self.order_counter
        }
        self.processes.append(p)

        self.process_table.insert(
            "", "end", iid=pid,
            values=(pid, arrival, burst, priority)
        )

        self.pid_var.set("")
        self.arrival_var.set("0")
        self.burst_var.set("5")
        self.priority_var.set("1")

    def remove_selected(self):
        selected = self.process_table.selection()
        if not selected:
            messagebox.showinfo("Select Process", "Select a process first.")
            return

        for pid in selected:
            self.processes = [
                p for p in self.processes if p["pid"] != pid
            ]
            self.process_table.delete(pid)

        self.results.clear()
        self.segments.clear()

    def clear_all(self):
        if not self.processes:
            return
        if not messagebox.askyesno(
            "Confirm", "Clear all processes and results?"
        ):
            return

        self.processes.clear()
        self.results.clear()
        self.segments.clear()
        self.order_counter = 0

        for item in self.process_table.get_children():
            self.process_table.delete(item)

        for item in self.result_table.get_children():
            self.result_table.delete(item)

        for item in self.comparison_table.get_children():
            self.comparison_table.delete(item)

        self.gantt_canvas.delete("all")
        self.gantt_canvas.configure(scrollregion=(0, 0, 1, 1))

        for label in self.metric_labels.values():
            label.config(text="—")

    def load_example(self):
        self.processes.clear()
        self.order_counter = 0

        for item in self.process_table.get_children():
            self.process_table.delete(item)

        examples = [
            ("P1", 0, 7, 2),
            ("P2", 2, 4, 1),
            ("P3", 4, 1, 3),
            ("P4", 5, 4, 2),
            ("P5", 6, 3, 1)
        ]

        for pid, arrival, burst, priority in examples:
            self.order_counter += 1
            p = {
                "pid": pid, "arrival": arrival, "burst": burst,
                "priority": priority, "order": self.order_counter
            }
            self.processes.append(p)
            self.process_table.insert(
                "", "end", iid=pid,
                values=(pid, arrival, burst, priority)
            )

        self.quantum_var.set("2")
        self.run_all()

    # --------------------------------------------------------
    # RESULTS AND GANTT CHART
    # --------------------------------------------------------

    def build_results(self):
        outer = tk.Frame(self.results_tab, bg=BG)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        toolbar = tk.Frame(outer, bg=BG)
        toolbar.pack(fill="x", pady=(0, 8))

        tk.Label(
            toolbar, text="Select Algorithm:",
            bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        self.algorithm_var = tk.StringVar(value="FCFS")
        combo = ttk.Combobox(
            toolbar, textvariable=self.algorithm_var,
            values=ALGORITHMS, state="readonly", width=18
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self.show_algorithm())

        self.button(
            toolbar, "Export CSV", self.export_csv, PURPLE
        ).pack(side="right")

        result_panel = self.panel(outer, "PROCESS PERFORMANCE", TEAL)
        result_panel.pack(fill="x", pady=(0, 8))

        body = tk.Frame(result_panel, bg=PANEL)
        body.pack(fill="x", padx=8, pady=8)

        cols = (
            "pid", "arrival", "burst", "completion",
            "turnaround", "waiting", "response"
        )
        self.result_table = ttk.Treeview(
            body, columns=cols, show="headings", height=5
        )

        headings = {
            "pid": "Process",
            "arrival": "Arrival",
            "burst": "Burst",
            "completion": "Completion",
            "turnaround": "Turnaround",
            "waiting": "Waiting",
            "response": "Response"
        }

        for col in cols:
            self.result_table.heading(col, text=headings[col])
            self.result_table.column(
                col, width=105, minwidth=75, anchor="center",
                stretch=True
            )

        sy = ttk.Scrollbar(
            body, orient="vertical", command=self.result_table.yview
        )
        sx = ttk.Scrollbar(
            body, orient="horizontal", command=self.result_table.xview
        )
        self.result_table.configure(
            yscrollcommand=sy.set, xscrollcommand=sx.set
        )
        self.result_table.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        body.grid_columnconfigure(0, weight=1)

        metrics = tk.Frame(outer, bg=BG)
        metrics.pack(fill="x", pady=(0, 8))

        self.metric_labels = {}
        metric_data = [
            ("avg_wait", "AVERAGE WAITING", BLUE),
            ("avg_tat", "AVERAGE TURNAROUND", PURPLE),
            ("avg_response", "AVERAGE RESPONSE", TEAL),
            ("total_time", "TOTAL EXECUTION", ORANGE)
        ]

        for key, title, color in metric_data:
            card = tk.Frame(
                metrics, bg=PANEL,
                highlightbackground=BORDER, highlightthickness=1
            )
            card.pack(side="left", fill="x", expand=True, padx=3)

            tk.Label(
                card, text=title, bg=color, fg="white",
                font=("Segoe UI", 8, "bold"), pady=6
            ).pack(fill="x")

            value = tk.Label(
                card, text="—", bg=PANEL, fg=TEXT,
                font=("Segoe UI", 13, "bold"), pady=8
            )
            value.pack()
            self.metric_labels[key] = value

        # GANTT CHART
        gantt_panel = self.panel(outer, "GANTT CHART", PURPLE)
        gantt_panel.pack(fill="both", expand=True)

        chart_body = tk.Frame(gantt_panel, bg=PANEL)
        chart_body.pack(fill="both", expand=True, padx=8, pady=8)

        self.gantt_canvas = tk.Canvas(
            chart_body,
            bg="#F8FAFC",
            height=180,
            highlightthickness=1,
            highlightbackground=BORDER,
            xscrollincrement=25
        )

        self.gantt_scrollbar = ttk.Scrollbar(
            chart_body,
            orient="horizontal",
            command=self.gantt_canvas.xview
        )

        self.gantt_canvas.configure(
            xscrollcommand=self.gantt_scrollbar.set
        )

        self.gantt_canvas.grid(row=0, column=0, sticky="nsew")
        self.gantt_scrollbar.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        chart_body.grid_rowconfigure(0, weight=1)
        chart_body.grid_columnconfigure(0, weight=1)

        self.gantt_canvas.bind(
            "<Shift-MouseWheel>",
            self.scroll_gantt
        )

        # Optional touchpad / horizontal mouse-wheel support on Windows.
        self.gantt_canvas.bind(
            "<MouseWheel>",
            self.scroll_gantt
        )

        # Redraw when the chart area changes size.
        self.gantt_canvas.bind(
            "<Configure>",
            lambda event: self.redraw_gantt_if_needed()
        )

    def scroll_gantt(self, event):
        if event.state & 0x0001:
            amount = -1 if event.delta > 0 else 1
            self.gantt_canvas.xview_scroll(amount * 3, "units")
            return "break"

        return None

    def run_all(self):
        if not self.processes:
            messagebox.showwarning(
                "No Processes", "Add processes or load the example."
            )
            return

        try:
            quantum = int(self.quantum_var.get())
            if quantum <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Quantum", "Quantum must be a positive integer."
            )
            return

        functions = {
            "FCFS": lambda: fcfs(self.processes),
            "SJF": lambda: sjf(self.processes),
            "Round Robin": lambda: round_robin(self.processes, quantum),
            "Priority": lambda: priority_scheduling(self.processes)
        }

        self.results.clear()
        self.segments.clear()

        for name, function in functions.items():
            self.segments[name] = function()
            self.results[name] = calculate_results(
                self.processes, self.segments[name]
            )

        self.show_algorithm()
        self.display_comparison()
        self.tabs.select(self.results_tab)

    def show_algorithm(self):
        name = self.algorithm_var.get()
        if name not in self.results:
            return

        for item in self.result_table.get_children():
            self.result_table.delete(item)

        rows = self.results[name]

        for r in rows:
            self.result_table.insert(
                "", "end",
                values=(
                    r["pid"], r["arrival"], r["burst"],
                    r["completion"], r["turnaround"],
                    r["waiting"], r["response"]
                )
            )

        count = len(rows)
        avg_wait = sum(r["waiting"] for r in rows) / count
        avg_tat = sum(r["turnaround"] for r in rows) / count
        avg_response = sum(r["response"] for r in rows) / count

        total_time = max(
            (s["end"] for s in self.segments[name]), default=0
        )

        self.metric_labels["avg_wait"].config(
            text=f"{avg_wait:.2f} units"
        )
        self.metric_labels["avg_tat"].config(
            text=f"{avg_tat:.2f} units"
        )
        self.metric_labels["avg_response"].config(
            text=f"{avg_response:.2f} units"
        )
        self.metric_labels["total_time"].config(
            text=f"{total_time} units"
        )

        self.draw_gantt(name)

    def redraw_gantt_if_needed(self):
        # Do not redraw repeatedly while the canvas is being resized.
        if self.algorithm_var.get() in self.segments:
            self.draw_gantt(self.algorithm_var.get(), keep_position=True)

    def draw_gantt(self, algorithm, keep_position=False):
        canvas = self.gantt_canvas

        # Preserve the current horizontal position when resizing.
        old_position = canvas.xview()[0] if keep_position else 0
        canvas.delete("all")

        segments = self.segments.get(algorithm, [])
        if not segments:
            canvas.configure(scrollregion=(0, 0, 1, 1))
            return

        palette = [
            "#2563EB", "#0F766E", "#7C3AED", "#EA580C",
            "#0891B2", "#BE185D", "#4D7C0F", "#9333EA",
            "#475569", "#B45309"
        ]

        process_colors = {
            p["pid"]: palette[i % len(palette)]
            for i, p in enumerate(self.processes)
        }

        # Use enough width for every timeline unit.
        # Long schedules therefore extend beyond the visible canvas
        # and can be inspected with the horizontal scrollbar.
        left = 35
        top = 48
        box_height = 62
        unit_width = 65
        total_time = max(s["end"] for s in segments)

        visible_width = max(canvas.winfo_width(), 700)
        timeline_width = total_time * unit_width
        chart_width = max(
            visible_width,
            left + timeline_width + 60
        )

        chart_height = max(canvas.winfo_height(), 180)

        canvas.create_text(
            left, 20,
            text=f"{algorithm} CPU Timeline",
            anchor="w",
            fill=NAVY,
            font=("Segoe UI", 12, "bold")
        )

        for seg in segments:
            x1 = left + seg["start"] * unit_width
            x2 = left + seg["end"] * unit_width
            pid = seg["pid"]

            if pid == "IDLE":
                color = "#CBD5E1"
                text_color = TEXT
            else:
                color = process_colors.get(pid, BLUE)
                text_color = "white"

            canvas.create_rectangle(
                x1, top, x2, top + box_height,
                fill=color,
                outline="white",
                width=2
            )

            # Keep the process name readable, even in short segments.
            canvas.create_text(
                (x1 + x2) / 2,
                top + box_height / 2,
                text=pid,
                fill=text_color,
                font=("Segoe UI", 10, "bold")
            )

            canvas.create_line(
                x1, top + box_height,
                x1, top + box_height + 8,
                fill=TEXT
            )
            canvas.create_text(
                x1, top + box_height + 18,
                text=str(seg["start"]),
                anchor="n",
                fill=TEXT,
                font=("Segoe UI", 9)
            )

        # Final timeline boundary.
        final_x = left + total_time * unit_width
        canvas.create_line(
            final_x, top + box_height,
            final_x, top + box_height + 8,
            fill=TEXT
        )
        canvas.create_text(
            final_x, top + box_height + 18,
            text=str(total_time),
            anchor="n",
            fill=TEXT,
            font=("Segoe UI", 9)
        )

        canvas.create_text(
            left, top + box_height + 43,
            text="Time (simulation units)",
            anchor="w",
            fill=MUTED,
            font=("Segoe UI", 9)
        )

        # Explicit scroll region: includes every process block and marker.
        canvas.configure(
            scrollregion=(0, 0, chart_width, chart_height)
        )
        canvas.xview_moveto(old_position)

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    def build_comparison(self):
        outer = tk.Frame(self.compare_tab, bg=BG)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        panel = self.panel(outer, "ALGORITHM COMPARISON", ORANGE)
        panel.pack(fill="both", expand=True)

        body = tk.Frame(panel, bg=PANEL)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        cols = (
            "algorithm", "waiting", "turnaround", "response", "total"
        )
        self.comparison_table = ttk.Treeview(
            body, columns=cols, show="headings", height=10
        )

        headings = {
            "algorithm": "Algorithm",
            "waiting": "Average Waiting",
            "turnaround": "Average Turnaround",
            "response": "Average Response",
            "total": "Total Execution"
        }

        for col in cols:
            self.comparison_table.heading(col, text=headings[col])
            self.comparison_table.column(
                col, width=170, minwidth=110,
                anchor="center", stretch=True
            )

        sy = ttk.Scrollbar(
            body, orient="vertical",
            command=self.comparison_table.yview
        )
        sx = ttk.Scrollbar(
            body, orient="horizontal",
            command=self.comparison_table.xview
        )
        self.comparison_table.configure(
            yscrollcommand=sy.set, xscrollcommand=sx.set
        )
        self.comparison_table.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.comparison_note = tk.Label(
            outer,
            text="Run all algorithms to compare results.",
            bg=BG, fg=MUTED, font=("Segoe UI", 10), anchor="w"
        )
        self.comparison_note.pack(fill="x", pady=8)

    def display_comparison(self):
        for item in self.comparison_table.get_children():
            self.comparison_table.delete(item)

        if not self.results:
            return

        for name in ALGORITHMS:
            rows = self.results[name]
            n = len(rows)

            waiting = sum(r["waiting"] for r in rows) / n
            turnaround = sum(r["turnaround"] for r in rows) / n
            response = sum(r["response"] for r in rows) / n
            total = max(s["end"] for s in self.segments[name])

            self.comparison_table.insert(
                "", "end",
                values=(
                    name, f"{waiting:.2f}", f"{turnaround:.2f}",
                    f"{response:.2f}", total
                )
            )

        best = min(
            ALGORITHMS,
            key=lambda name: sum(
                r["waiting"] for r in self.results[name]
            ) / len(self.results[name])
        )

        self.comparison_note.config(
            text=f"Lowest average waiting time for this input: {best}.",
            fg=GREEN
        )

    # --------------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------------

    def export_csv(self):
        if not self.results:
            messagebox.showwarning(
                "No Results", "Run the algorithms before exporting."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="cpu_scheduling_results.csv"
        )

        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Algorithm", "Process ID", "Arrival Time",
                    "Burst Time", "Priority", "Completion Time",
                    "Turnaround Time", "Waiting Time", "Response Time"
                ])

                for name in ALGORITHMS:
                    for r in self.results[name]:
                        writer.writerow([
                            name, r["pid"], r["arrival"], r["burst"],
                            r["priority"], r["completion"],
                            r["turnaround"], r["waiting"], r["response"]
                        ])

            messagebox.showinfo(
                "Success", f"CSV file saved successfully:\n{path}"
            )
        except OSError as error:
            messagebox.showerror(
                "Export Error", f"Could not save the file:\n{error}"
            )

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    def build_help(self):
        outer = tk.Frame(self.help_tab, bg=BG)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        panel = self.panel(outer, "HELP & FORMULAS", BLUE)
        panel.pack(fill="both", expand=True)

        text = (
            "FCFS — First Come First Served\n"
            "Processes execute in arrival order. Non-preemptive.\n\n"
            "SJF — Shortest Job First\n"
            "Chooses the available process with the shortest burst time. "
            "Non-preemptive.\n\n"
            "Round Robin\n"
            "Each process receives CPU time up to the time quantum. "
            "Unfinished processes return to the ready queue.\n\n"
            "Priority Scheduling\n"
            "The available process with the smallest priority number runs "
            "first. Non-preemptive.\n\n"
            "FORMULAS\n"
            "Turnaround Time = Completion Time − Arrival Time\n"
            "Waiting Time = Turnaround Time − Burst Time\n"
            "Average Waiting Time = Total Waiting Time ÷ Process Count\n"
            "Average Turnaround Time = Total Turnaround Time ÷ Process Count\n"
            "Response Time = First CPU Start Time − Arrival Time\n\n"
            "UNITS\n"
            "Times are logical simulation units, not necessarily real seconds.\n"
            "Process IDs and priority numbers are unitless.\n\n"
            "HOW TO USE\n"
            "1. Add processes or click Load Example.\n"
            "2. Set the Round Robin quantum.\n"
            "3. Click Run All Algorithms.\n"
            "4. Choose an algorithm from the Results tab dropdown.\n"
            "5. Use the scrollbar beneath the Gantt chart to view the full "
            "timeline, including processes beyond the visible area.\n"
            "6. Export the results to CSV if required."
        )

        tk.Label(
            panel,
            text=text,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            justify="left",
            anchor="nw",
            padx=18,
            pady=15
        ).pack(fill="both", expand=True)


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulingApp(root)
    root.mainloop()
