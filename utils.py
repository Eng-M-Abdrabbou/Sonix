# utils.py

import os
import platform

def apply_cuda_fix():
    """
    Programmatically adds the CUDA Toolkit's bin directory to the system's PATH
    to solve the 'cublas...dll not found' error on Windows.
    """
    if platform.system() != "Windows":
        return

    # Assuming CUDA 12.9 is installed at the default location.
    # Adjust the version number if you have a different one.
    cuda_version = "12.9"
    default_cuda_path = f"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v{cuda_version}"
    bin_path = os.path.join(default_cuda_path, 'bin')

    if os.path.exists(bin_path):
        print(f"DEBUG: Found CUDA bin path: {bin_path}")
        os.environ['PATH'] = bin_path + os.pathsep + os.environ['PATH']
        
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(bin_path)
                print("DEBUG: Successfully added CUDA bin path to DLL search paths.")
            except Exception as e:
                print(f"DEBUG: Could not add DLL directory: {e}")
        print("DEBUG: CUDA path fix applied.")
    else:
        print(f"WARNING: CUDA path not found at '{default_cuda_path}'. DLL errors may occur.")
        print("WARNING: Please verify your CUDA Toolkit installation path.")

def initialize_device(initial_device_pref):
    """
    Checks for CUDA availability and returns the appropriate device.
    Falls back to CPU if CUDA is not available or an error occurs.
    """
    # Handle potential OpenMP conflicts
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    device = initial_device_pref
    if device == "cuda":
        try:
            import torch
            if not torch.cuda.is_available():
                print("--------------------------------------------------------------------")
                print("WARNING: CUDA selected, but torch reports CUDA not available!")
                print("Falling back to CPU. Performance will be significantly lower.")
                print("--------------------------------------------------------------------")
                device = "cpu"
            else:
                print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
        except ImportError:
            print("--------------------------------------------------------------------")
            print("WARNING: PyTorch not found. It is required for CUDA.")
            print("Falling back to CPU.")
            print("--------------------------------------------------------------------")
            device = "cpu"
        except Exception as e:
            print(f"ERROR: An error occurred during CUDA check: {e}")
            print("Falling back to CPU.")
            device = "cpu"

    print(f"DEBUG: Final device for transcription: {device}")
    return device