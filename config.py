# config.py

# --- Model Configuration ---
MODEL_SIZE = "small.en"
COMPUTE_TYPE = "int8_float16"
INITIAL_DEVICE = "cuda"

# --- Audio Settings ---
SAMPLERATE = 16000
CHANNELS = 1
DTYPE = 'float32'
BLOCKSIZE_MS = 100
BLOCKSIZE_FRAMES = int(SAMPLERATE * BLOCKSIZE_MS / 1000)

# --- NEW: Manual Streaming Configuration ---
# How many seconds of audio to process at a time.
# A smaller value (e.g., 1.0) is more responsive, but a larger value (e.g., 3.0)
# may give the model better context and improve accuracy. 2.0 is a good balance.
CHUNK_DURATION_S = 2.0

# --- Transcription Settings ---
LANGUAGE = "en"
BEAM_SIZE = 1

# --- VAD (Voice Activity Detection) Parameters ---
# These are still useful for filtering silence within each chunk.
VAD_PARAMETERS = dict(
    threshold=0.4,
    min_speech_duration_ms=100,
    max_speech_duration_s=10,
    min_silence_duration_ms=200,
    speech_pad_ms=100
)