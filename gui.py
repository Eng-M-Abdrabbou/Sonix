# gui.py

import tkinter as tk
from tkinter import scrolledtext, ttk, font
import threading
from transcription_engine import TranscriptionEngine

class RealTimeTranscriptionApp:
    def __init__(self, root_window, device):
        print("DEBUG: GUI - Initializing...")
        self.root = root_window
        self.root.title("Sonix")
        self.root.geometry("900x700")

        self.is_closing = False
        
        self._configure_styles()
        self._create_widgets()

        print("DEBUG: GUI - Initializing TranscriptionEngine...")
        self.transcription_engine = TranscriptionEngine(self.handle_engine_updates, device)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("DEBUG: GUI - Initialization complete.")

    def _configure_styles(self):
        self.style = ttk.Style()
        try:
            if 'clam' in self.style.theme_names():
                self.style.theme_use('clam')
        except tk.TclError:
            print("DEBUG: 'clam' theme not available, using default.")

        font_name = "Segoe UI" if self.root.tk.call('tk', 'windowingsystem') == 'win32' else "Noto Sans"
        
        self.style.configure("TButton", padding=8, relief="flat", font=(font_name, 11, "bold"))
        self.style.configure("TLabel", padding=5, font=(font_name, 11))
        self.style.configure("Status.TLabel", padding=(10, 5), font=(font_name, 10), relief=tk.GROOVE, borderwidth=1)
        
        self.style.map("Stop.TButton", background=[('active', '#E53935'),('!disabled', '#F44336')], foreground=[('!disabled', 'white')])
        self.style.map("Start.TButton", background=[('active', '#43A047'),('!disabled', '#4CAF50')], foreground=[('!disabled', 'white')])
        
        self.font_main_text = (font_name, 16)
        self.font_status_bar = (font_name, 10)

    def _create_widgets(self):
        self.status_bar = ttk.Label(self.root, text="Press START to begin transcription.", anchor=tk.W, style="Status.TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 2))

        controls_frame = ttk.Frame(self.root, padding=(10, 5, 10, 5))
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        self.start_button = ttk.Button(controls_frame, text="▶ START", command=self.start_transcription, style="Start.TButton", width=15)
        self.start_button.pack(side=tk.LEFT, padx=(10,5), pady=5)

        self.stop_button = ttk.Button(controls_frame, text="■ STOP", command=self.stop_transcription, state=tk.DISABLED, style="Stop.TButton", width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.clear_button = ttk.Button(controls_frame, text="CLEAR TEXT", command=self.clear_text_area, width=15)
        self.clear_button.pack(side=tk.RIGHT, padx=(5,10), pady=5)

        text_area_frame = ttk.Frame(self.root, padding=(15, 15, 15, 15))
        text_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.text_area = scrolledtext.ScrolledText(
            text_area_frame, wrap=tk.WORD, state='disabled',
            font=self.font_main_text, padx=15, pady=15, relief=tk.SOLID, bd=1,
            background="#F5F5F5", foreground="#212121"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def handle_engine_updates(self, type, data):
        if self.is_closing: return
        
        if type == "status":
            self.status_bar.config(text=data)
        elif type == "append_text":
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, data)
            self.text_area.config(state='disabled')
            self.text_area.see(tk.END)

    def start_transcription(self):
        if self.transcription_engine.is_running: return
        self.status_bar.config(text="Initializing engine...")
        self.root.update_idletasks()
        threading.Thread(target=self._start_engine_thread, daemon=True).start()

    def _start_engine_thread(self):
        try:
            self.transcription_engine.start()
            if self.transcription_engine.is_running:
                 self.root.after(0, self._update_ui_for_start)
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Startup Error: {e}"))
            self.root.after(0, self._update_ui_for_stop)

    def stop_transcription(self):
        if not self.transcription_engine.is_running: return
        self.status_bar.config(text="Stopping engine...")
        self.root.update_idletasks()
        threading.Thread(target=self._stop_engine_thread, daemon=True).start()

    def _stop_engine_thread(self):
        self.transcription_engine.stop()
        self.root.after(0, self._update_ui_for_stop)

    def _update_ui_for_start(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def _update_ui_for_stop(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def clear_text_area(self):
        self.text_area.config(state='normal')
        self.text_area.delete('1.0', tk.END)
        self.text_area.config(state='disabled')

    def on_closing(self):
        print("DEBUG: GUI - Closing application...")
        if self.is_closing: return
        self.is_closing = True

        if self.transcription_engine.is_running:
            stop_thread = threading.Thread(target=self.transcription_engine.stop, daemon=True)
            stop_thread.start()
            stop_thread.join(timeout=2.0)

        print("DEBUG: GUI - Destroying root window.")
        self.root.destroy()