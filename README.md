# PiMonitor

A lightweight Raspberry Pi system monitor written in Python using Tkinter.

Designed for Raspberry Pi 5 running Raspberry Pi OS Trixie.

## Features

- CPU temperature and utilization
- System memory usage and available memory
- SD card usage
- Collapsible system information including hostname, IP address, operating system and kernel
- Automatic updates every two seconds
- Lightweight graphical interface without a terminal window

## Requirements

- Python 3
- Tkinter (`python3-tk`)

## Desktop Launcher

Install the desktop launcher

```bash
cp pimonitor.desktop ~/.local/share/applications/
```

## Running

```bash
python3 pimonitor.py
```

The program can also be launched using the desktop launcher.
