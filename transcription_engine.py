# transcription_engine.py

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import threading
import queue
import time
import torch

import config

class TranscriptionEngine:
    def __init__(self, ui_update_callback, device):
        self.ui_update_callback = ui_update_callback
        self.device = device
        self.audio_queue = queue.Queue()
        self.model = None
        self.is_running = False
        self.transcription_thread = None
        self.stream = None

    def _load_model(self):
        try:
            status_msg = f"Loading Whisper: {config.MODEL_SIZE} ({config.COMPUTE_TYPE}) on {self.device}..."
            self.ui_update_callback("status", status_msg)
            self.model = WhisperModel(config.MODEL_SIZE, device=self.device, compute_type=config.COMPUTE_TYPE)
            print("Model loaded successfully.")
            self.ui_update_callback("status", f"Model: {config.MODEL_SIZE} ({config.COMPUTE_TYPE}) on {self.device} - Ready. Listening...")
        except Exception as e:
            self.ui_update_callback("status", f"Error: Could not load model! Check console. ({e})")
            raise

    def _audio_capture_callback(self, indata, frames, time_info, status):
        if status:
            print(f"AudioCallback status: {status}", flush=True)
        if self.is_running:
            self.audio_queue.put(indata.copy())

    def _transcription_loop(self):
        print("DEBUG: Transcription loop started (Manual Chunking Mode).")
        while self.is_running:
            try:
                # 1. Gather a chunk of audio
                chunk_audio_data = []
                chunk_start_time = time.perf_counter()
                
                # Collect audio data for the configured duration
                while time.perf_counter() - chunk_start_time < config.CHUNK_DURATION_S:
                    if not self.is_running: break
                    try:
                        audio_data = self.audio_queue.get(timeout=0.1)
                        chunk_audio_data.append(audio_data)
                    except queue.Empty:
                        continue
                
                if not self.is_running or not chunk_audio_data:
                    continue

                # 2. Concatenate the audio data into a single NumPy array
                audio_chunk = np.concatenate(chunk_audio_data).flatten()

                # 3. Transcribe the complete chunk
                segments, _ = self.model.transcribe(
                    audio_chunk,
                    language=config.LANGUAGE,
                    beam_size=config.BEAM_SIZE,
                    word_timestamps=True,
                    vad_filter=True,
                    vad_parameters=config.VAD_PARAMETERS,
                )

                # 4. Process and send the results to the GUI
                transcribed_text = "".join(segment.text for segment in segments)
                if transcribed_text:
                    self.ui_update_callback("append_text", transcribed_text)

            except Exception as e:
                if self.is_running:
                    print(f"FATAL: Transcription loop error: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                break # Exit the loop on a fatal error

        print("DEBUG: Transcription loop finished.")

    def start(self):
        if self.is_running: return
        try: self._load_model()
        except Exception: return

        self.is_running = True
        while not self.audio_queue.empty():
            try: self.audio_queue.get_nowait()
            except queue.Empty: break

        try:
            print("DEBUG: Opening audio stream...")
            self.stream = sd.InputStream(
                samplerate=config.SAMPLERATE, blocksize=config.BLOCKSIZE_FRAMES,
                channels=config.CHANNELS, dtype=config.DTYPE,
                callback=self._audio_capture_callback
            )
            self.stream.start()
            print("DEBUG: Audio stream started.")
        except Exception as e:
            self.ui_update_callback("status", f"Error: Audio stream failed! Check console. ({e})")
            self.is_running = False
            return

        self.transcription_thread = threading.Thread(target=self._transcription_loop, daemon=True)
        self.transcription_thread.start()
        print("Transcription engine started.")

    def stop(self):
        if not self.is_running: return
        print("Stopping transcription engine...")
        self.is_running = False

        if self.transcription_thread:
            self.transcription_thread.join(timeout=1.5)
        
        if self.stream:
            try:
                self.stream.stop(); self.stream.close()
                print("DEBUG: Audio stream stopped and closed.")
            except Exception as e:
                print(f"Error stopping audio stream: {e}")
        
        if self.device == "cuda" and 'torch' in globals() and torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("CUDA cache cleared.")

        self.ui_update_callback("status", "Engine Stopped.")
        print("Transcription engine stopped.")