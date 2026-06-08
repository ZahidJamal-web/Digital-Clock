import time
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Premium Palette Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RealisticUltimateClock(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("Chronos Dashboard Pro")
        self.geometry("520x460")
        self.resizable(False, False)
        self.configure(fg_color="#0F0F11")

        # --- STATE VARIABLES ---
        self.sw_running = False
        self.sw_start_time = 0.0
        self.sw_elapsed_time = 0.0
        self.laps = []

        self.alarm_time = None
        self.alarm_active = False
        self.is_ringing = False

        # --- UI TABS ---
        self.tabs = ctk.CTkTabview(self, width=480, height=420, 
                                  segmented_button_fg_color="#18181C",
                                  segmented_button_selected_color="#2563EB",
                                  segmented_button_selected_hover_color="#1D4ED8")
        self.tabs.pack(padx=20, pady=10)

        self.tab_clock = self.tabs.add("Clock")
        self.tab_stopwatch = self.tabs.add("Stopwatch")
        self.tab_alarm = self.tabs.add("Alarm")

        self.setup_clock_tab()
        self.setup_stopwatch_tab()
        self.setup_alarm_tab()

        # Engine loops
        self.update_clock()
        self.check_alarm()

    # ==========================================
    # 1. REALISTIC CLOCK & WORLD CLOCK
    # ==========================================
    def setup_clock_tab(self):
        # Local Date
        self.date_label = ctk.CTkLabel(self.tab_clock, text="", font=("Segoe UI", 16, "bold"), text_color="#A1A1AA")
        self.date_label.pack(pady=(20, 5))

        # Main Time Layout
        self.time_frame = ctk.CTkFrame(self.tab_clock, fg_color="transparent")
        self.time_frame.pack(pady=5)

        self.time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=("Segoe UI", 68, "bold"), text_color="#FFFFFF")
        self.time_label.pack(side="left", padx=(10, 5))

        self.side_frame = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        self.side_frame.pack(side="left", fill="y", pady=15)

        self.ampm_label = ctk.CTkLabel(self.side_frame, text="AM", font=("Segoe UI", 14, "bold"), text_color="#10B981")
        self.ampm_label.pack(anchor="w")

        self.sec_label = ctk.CTkLabel(self.side_frame, text="00", font=("Segoe UI", 22, "bold"), text_color="#3B82F6")
        self.sec_label.pack(anchor="w")

        # Progress bar tracking the minute
        self.progress_bar = ctk.CTkProgressBar(self.tab_clock, width=380, height=6, corner_radius=10,
                                               progress_color="#3B82F6", fg_color="#27272A")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=15)

        # --- REALISTIC ADDITION: World Clock Frame ---
        self.world_frame = ctk.CTkFrame(self.tab_clock, fg_color="#18181C", corner_radius=8, width=380, height=60)
        self.world_frame.pack(pady=(10, 0))
        self.world_frame.pack_propagate(False)

        self.world_title = ctk.CTkLabel(self.world_frame, text="LONDON (GMT / UTC)", font=("Segoe UI", 11, "bold"), text_color="#71717A")
        self.world_title.pack(anchor="w", padx=15, pady=(8, 0))
        
        self.world_time_label = ctk.CTkLabel(self.world_frame, text="00:00:00 GMT", font=("Segoe UI", 16, "bold"), text_color="#E4E4E7")
        self.world_time_label.pack(anchor="w", padx=15)

        # --- REALISTIC ADDITION: Hourly Chime Feature Toggle ---
        self.chime_switch = ctk.CTkSwitch(self.tab_clock, text="Hourly Flash Chime", font=("Segoe UI", 12), text_color="#A1A1AA")
        self.chime_switch.pack(pady=(20, 0))

    def update_clock(self):
        now = datetime.now()
        
        # Local updates
        self.time_label.configure(text=now.strftime("%I:%M"))
        self.sec_label.configure(text=now.strftime("%S"))
        self.ampm_label.configure(text=now.strftime("%p"))
        self.date_label.configure(text=now.strftime("%A, %B %d, %Y").upper())
        self.progress_bar.set(int(now.strftime("%S")) / 60.0)

        # Dynamic aesthetic shift
        self.ampm_label.configure(text_color="#F59E0B" if now.strftime("%p") == "PM" else "#10B981")

        # World Clock Calculations (UTC example)
        utc_now = datetime.utcnow()
        self.world_time_label.configure(text=utc_now.strftime("%I:%M:%S %p UTC"))

        # Hourly Chime trigger rule (Flashes progress bar color briefly at minute zero)
        if self.chime_switch.get() and now.minute == 0 and now.second < 3:
            self.progress_bar.configure(progress_color="#EF4444") # Crimson Flash
        else:
            self.progress_bar.configure(progress_color="#3B82F6")

        self.after(100, self.update_clock)


    # ==========================================
    # 2. STOPWATCH WITH LAP RECORDER
    # ==========================================
    def setup_stopwatch_tab(self):
        self.sw_label = ctk.CTkLabel(self.tab_stopwatch, text="00:00.00", font=("Segoe UI", 54, "bold"), text_color="#FFFFFF")
        self.sw_label.pack(pady=(20, 15))

        # Control row
        self.sw_btn_frame = ctk.CTkFrame(self.tab_stopwatch, fg_color="transparent")
        self.sw_btn_frame.pack(pady=5)

        self.sw_start_btn = ctk.CTkButton(self.sw_btn_frame, text="Start", width=90, fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 13, "bold"), command=self.start_stopwatch)
        self.sw_start_btn.pack(side="left", padx=5)

        self.sw_lap_btn = ctk.CTkButton(self.sw_btn_frame, text="Lap", width=90, fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 13, "bold"), command=self.record_lap, state="disabled")
        self.sw_lap_btn.pack(side="left", padx=5)

        self.sw_reset_btn = ctk.CTkButton(self.sw_btn_frame, text="Reset", width=90, fg_color="#EF4444", hover_color="#DC2626", font=("Segoe UI", 13, "bold"), command=self.reset_stopwatch)
        self.sw_reset_btn.pack(side="left", padx=5)

        # --- REALISTIC ADDITION: Scrollable Lap Window ---
        self.lap_box = ctk.CTkTextbox(self.tab_stopwatch, width=380, height=140, fg_color="#18181C", border_color="#27272A", text_color="#D4D4D8", font=("Consolas", 13))
        self.lap_box.pack(pady=15)
        self.lap_box.insert("0.0", " Lap History will generate here...\n")
        self.lap_box.configure(state="disabled")

    def start_stopwatch(self):
        if not self.sw_running:
            self.sw_running = True
            self.sw_start_btn.configure(text="Pause", fg_color="#F59E0B", hover_color="#D97706")
            self.sw_lap_btn.configure(state="normal")
            self.sw_start_time = time.time() - self.sw_elapsed_time
            self.update_stopwatch()
        else:
            self.sw_running = False
            self.sw_start_btn.configure(text="Resume", fg_color="#10B981", hover_color="#059669")
            self.sw_lap_btn.configure(state="disabled")

    def record_lap(self):
        if self.sw_running:
            lap_num = len(self.laps) + 1
            current_stamp = self.sw_label.get()
            self.laps.append(f"Lap {lap_num:02d} ---------> {current_stamp}")
            
            # Refresh text box strings
            self.lap_box.configure(state="normal")
            self.lap_box.delete("1.0", tk.END)
            for lap in reversed(self.laps):
                self.lap_box.insert(tk.END, f" {lap}\n")
            self.lap_box.configure(state="disabled")

    def reset_stopwatch(self):
        self.sw_running = False
        self.sw_elapsed_time = 0.0
        self.laps.clear()
        self.sw_label.configure(text="00:00.00")
        self.sw_start_btn.configure(text="Start", fg_color="#10B981", hover_color="#059669")
        self.sw_lap_btn.configure(state="disabled")
        
        self.lap_box.configure(state="normal")
        self.lap_box.delete("1.0", tk.END)
        self.lap_box.insert("0.0", " Lap History cleared.\n")
        self.lap_box.configure(state="disabled")

    def update_stopwatch(self):
        if self.sw_running:
            self.sw_elapsed_time = time.time() - self.sw_start_time
            minutes = int(self.sw_elapsed_time // 60)
            seconds = int(self.sw_elapsed_time % 60)
            centiseconds = int((self.sw_elapsed_time - int(self.sw_elapsed_time)) * 100)
            self.sw_label.configure(text=f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}")
            self.after(10, self.update_stopwatch)


    # ==========================================
    # 3. ALARM WITH REALISTIC SNOOZE FUNCTION
    # ==========================================
    def setup_alarm_tab(self):
        self.alarm_frame = ctk.CTkFrame(self.tab_alarm, fg_color="transparent")
        self.alarm_frame.pack(pady=(30, 15))

        # Standard Comboboxes Configuration
        self.hour_combobox = ctk.CTkComboBox(self.alarm_frame, values=[f"{i:02d}" for i in range(1, 13)], width=70)
        self.hour_combobox.pack(side="left", padx=4)

        self.min_combobox = ctk.CTkComboBox(self.alarm_frame, values=[f"{i:02d}" for i in range(60)], width=70)
        self.min_combobox.pack(side="left", padx=4)

        self.ampm_combobox = ctk.CTkComboBox(self.alarm_frame, values=["AM", "PM"], width=80)
        self.ampm_combobox.pack(side="left", padx=4)

        self.alarm_status_label = ctk.CTkLabel(self.tab_alarm, text="No active alarm configured", font=("Segoe UI", 13, "italic"), text_color="#71717A")
        self.alarm_status_label.pack(pady=5)

        self.alarm_btn = ctk.CTkButton(self.tab_alarm, text="Activate Alarm", width=160, font=("Segoe UI", 13, "bold"), command=self.toggle_alarm)
        self.alarm_btn.pack(pady=10)

        # --- REALISTIC ADDITION: Contextual Snooze Interaction Module ---
        self.snooze_btn = ctk.CTkButton(self.tab_alarm, text="Snooze (5 Mins)", fg_color="#F59E0B", hover_color="#D97706",
                                        text_color="#000000", font=("Segoe UI", 13, "bold"), command=self.trigger_snooze, state="disabled")
        self.snooze_btn.pack(pady=5)

    def toggle_alarm(self):
        if not self.alarm_active:
            h, m, p = self.hour_combobox.get(), self.min_combobox.get(), self.ampm_combobox.get()
            self.alarm_time = f"{h}:{m} {p}"
            self.alarm_active = True
            self.alarm_status_label.configure(text=f"🔔 Ringing at {self.alarm_time}", text_color="#6366F1", font=("Segoe UI", 13, "bold"))
            self.alarm_btn.configure(text="Dismiss Alarm", fg_color="#EF4444", hover_color="#DC2626")
        else:
            self.cancel_alarm_state()

    def cancel_alarm_state(self):
        self.alarm_active = False
        self.is_ringing = False
        self.alarm_time = None
        self.alarm_status_label.configure(text="No active alarm configured", text_color="#71717A", font=("Segoe UI", 13, "italic"))
        self.alarm_btn.configure(text="Activate Alarm", fg_color="#3B82F6", hover_color="#2563EB")
        self.snooze_btn.configure(state="disabled")

    def trigger_snooze(self):
        if self.is_ringing:
            self.is_ringing = False # Stops current sound threading loop
            
            # Postpone alarm reference target forward by exactly 5 minutes
            now = datetime.now()
            snooze_target = now + timedelta(minutes=5)
            self.alarm_time = snooze_target.strftime("%I:%M %p")
            
            self.alarm_active = True
            self.alarm_status_label.configure(text=f"💤 Snoozed until {self.alarm_time}", text_color="#F59E0B")
            self.alarm_btn.configure(text="Dismiss Alarm", fg_color="#EF4444", hover_color="#DC2626")
            self.snooze_btn.configure(state="disabled")

    def check_alarm(self):
        if self.alarm_active and self.alarm_time:
            now_str = datetime.now().strftime("%I:%M %p")
            if now_str == self.alarm_time and not self.is_ringing:
                self.alarm_active = False
                self.is_ringing = True
                self.snooze_btn.configure(state="normal")
                
                # Active firing system inside thread
                threading.Thread(target=self.fire_audio_loop, daemon=True).start()
                
        self.after(1000, self.check_alarm)

    def fire_audio_loop(self):
        # Audio loop runs dynamically while state validates positive execution
        while self.is_ringing:
            try:
                import winsound
                winsound.Beep(1200, 400)
                time.sleep(0.3)
            except ImportError:
                print("\a[ALARM RINGING] Press Snooze or Dismiss")
                time.sleep(1)
                
        # Fire structural window alert on main thread context when thread steps out
        if not self.alarm_active and not self.is_ringing: 
            pass # Gracefully closed via snooze/dismiss choices


if __name__ == "__main__":
    app = RealisticUltimateClock()
    app.mainloop()