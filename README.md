# Chronos Dashboard Pro 🕰️

A premium, feature-rich desktop digital clock suite built with Python. Featuring an ultra-modern, dark-themed UI, this application integrates a live clock, world clock, precision stopwatch with lap logging, and an advanced alarm system with snooze functionality—all bundled into a single, high-performance file.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 1. Neo-Digital Clock
* **Dynamic Time & Date:** Displays local 12-hour formatted time along with a high-visibility capitalized date string.
* **Minute Progress Visualizer:** A sleek, dedicated progress bar maps out passing seconds ($Seconds / 60$) in real time.
* **Integrated World Clock:** Keeps track of standard **UTC / GMT** time continuously in an independent preview panel.
* **Hourly Flash Chime:** An optional switch that flashes the progress bar crimson for three seconds at the top of every hour.

### 2. Precision Stopwatch
* **Absolute Timestamping:** Uses Python's native `time.time()` tracking to map elapsed duration down to the **exact centisecond ($0.01$s)**, ignoring CPU thread lags.
* **Lap Memory Log:** Capture infinite split-second intervals while the timer runs, populating a reverse-sorted, scrollable lap board.

### 3. Smart Alarm Suite
* **Threaded Audio Engine:** The alarm trigger runs inside an independent background thread. The app stays completely responsive while the audio sounds.
* **Contextual Snooze:** Hitting "Snooze" triggers an algorithmic temporal shift ($\text{Target} = \text{Current Time} + 5 \text{ Minutes}$) to silence the sound and auto-rearm the system.

---

## 🛠️ Prerequisites & Installation

Make sure you have Python 3.8 or higher installed on your computer.

1. **Clone or Download the script:**
   Save the main script file as `clock_dashboard.py`.

2. **Install dependencies:**
   The interface requires the modern `customtkinter` library:
   ```bash
   pip install customtkinter
