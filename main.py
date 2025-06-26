# main.py

import tkinter as tk
import traceback

import utils
import config
from gui import RealTimeTranscriptionApp

def main():
    """
    Main function to initialize and run the transcription application.
    """
    print("DEBUG: Main - Application starting...")
    
    # 1. Apply environment fixes (like CUDA path)
    utils.apply_cuda_fix()
    
    # 2. Determine the processing device (CUDA or CPU)
    device = utils.initialize_device(config.INITIAL_DEVICE)
    
    # 3. Set up and run the GUI
    root = None
    try:
        print("DEBUG: Main - Initializing Tkinter root...")
        root = tk.Tk()
        
        # Pass the device to the GUI, which then passes it to the engine
        app = RealTimeTranscriptionApp(root, device)
        
        print("DEBUG: Main - Starting Tkinter mainloop.")
        root.mainloop()
        print("DEBUG: Main - Tkinter mainloop finished.")
        
    except Exception as e:
        print(f"!!!!!!!!!! FATAL ERROR in main: {e} !!!!!!!!!!")
        traceback.print_exc()
        
    finally:
        print("DEBUG: Main - Application exited.")

if __name__ == '__main__':
    main()