
#!/usr/bin/env python3
# Pi Monitor - Raspberry Pi system dashboard

import tkinter as tk
from tkinter import ttk
import platform
import socket
import subprocess
import os
import shutil


UPDATE_INTERVAL = 2000  # milliseconds


def command(args):
    """Run a system command and return its output."""
    try:
        return subprocess.check_output(
            args, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "Unknown"


def system_info():
    """Collect static system information."""
    info = {}

    info["Hostname"] = socket.gethostname()

    addresses = command(["hostname", "-I"]).split()
    info["IP address"] = addresses[0] if addresses else "Unknown"

    info["Model"] = command(["cat", "/proc/device-tree/model"])
    info["Desktop"] = os.environ.get("XDG_SESSION_TYPE", "Unknown")
    info["Kernel"] = platform.release()
    info["Architecture"] = platform.machine()
    info["Kernel type"] = platform.architecture()[0]

    # Total system memory
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                kb = int(line.split()[1])
                info["Total memory"] = f"{kb / 1024 / 1024:.1f} GiB"
                break

    # Operating system
    info["Operating system"] = "Unknown"
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    info["Operating system"] = (
                        line.split("=", 1)[1].strip().strip('"')
                    )
                    break
    except OSError:
        pass

    return info


def cpu_times():
    """Read total and idle CPU time from /proc/stat."""
    with open("/proc/stat") as f:
        values = list(map(int, f.readline().split()[1:]))

    idle = values[3] + values[4]
    total = sum(values)
    return total, idle


def cpu_temperature():
    """Read CPU temperature in degrees Celsius."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read()) / 1000
    except (OSError, ValueError):
        return None


def memory_usage():
    """Read memory information from /proc/meminfo."""
    mem = {}

    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":", 1)
            mem[key] = int(value.split()[0])

    total = mem["MemTotal"]
    available = mem["MemAvailable"]
    used = total - available

    return (
        used / 1024 / 1024,
        available / 1024 / 1024,
        total / 1024 / 1024
    )


def disk_usage():
    """Return percentage used on the root filesystem."""
    total, used, free = shutil.disk_usage("/")
    return 100 * used / total


# Main window
root = tk.Tk()
root.title("Pi Monitor")
root.geometry("500x350")
root.minsize(450, 300)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(
    frame,
    text="Raspberry Pi System Monitor",
    font=("Sans", 16, "bold")
).pack(anchor="w", pady=(0, 15))


# Live measurements
live_frame = ttk.LabelFrame(
    frame, text="Live system status", padding=12
)
live_frame.pack(fill="x", pady=(0, 15))

live_labels = {}

for name in (
    "CPU temperature",
    "CPU usage",
    "Memory used",
    "Memory available",
    "SD card usage"
):
    row = ttk.Frame(live_frame)
    row.pack(fill="x", pady=4)

    ttk.Label(
        row, text=name + ":", width=20
    ).pack(side="left")

    value_label = ttk.Label(
        row, text="—", font=("Sans", 11, "bold")
    )
    value_label.pack(side="left")

    live_labels[name] = value_label


# Collapsible system information
details_visible = tk.BooleanVar(value=False)

details = ttk.Frame(frame)


def toggle_details():
    if details_visible.get():
        details.pack_forget()
        details_visible.set(False)
        toggle_button.config(text="Show system information ▾")
        root.geometry("500x350")
    else:
        details.pack(fill="x", pady=10)
        details_visible.set(True)
        toggle_button.config(text="Hide system information ▴")
        root.geometry("500x600")


toggle_button = ttk.Button(
    frame,
    text="Show system information ▾",
    command=toggle_details
)
toggle_button.pack(fill="x")

for name, value in system_info().items():
    row = ttk.Frame(details)
    row.pack(fill="x", pady=3)

    ttk.Label(
        row, text=name + ":", width=19
    ).pack(side="left")

    ttk.Label(
        row, text=value
    ).pack(side="left")


# Periodic updates
previous_cpu = cpu_times()


def update_status():
    global previous_cpu

    # CPU utilization
    current_cpu = cpu_times()
    delta_total = current_cpu[0] - previous_cpu[0]
    delta_idle = current_cpu[1] - previous_cpu[1]
    previous_cpu = current_cpu

    if delta_total > 0:
        usage = 100 * (1 - delta_idle / delta_total)
        live_labels["CPU usage"].config(text=f"{usage:.1f} %")

    # CPU temperature
    temperature = cpu_temperature()
    if temperature is not None:
        live_labels["CPU temperature"].config(
            text=f"{temperature:.1f} °C"
        )

    # Memory
    used, available, total = memory_usage()
    live_labels["Memory used"].config(
        text=f"{used:.2f} / {total:.2f} GiB"
    )
    live_labels["Memory available"].config(
        text=f"{available:.2f} GiB"
    )

    # SD card
    live_labels["SD card usage"].config(
        text=f"{disk_usage():.1f} %"
    )

    root.after(UPDATE_INTERVAL, update_status)


# Start updates and event loop
root.after(UPDATE_INTERVAL, update_status)
root.mainloop()
