"""Decodifica audio condivisa (vedi reel.py)."""

def load_audio(path, a=None, b=None):
    """Audio 16 kHz mono float32 via ffmpeg (evita incompatibilità faster-whisper/PyAV)."""
    import subprocess, numpy as np
    cmd = ['ffmpeg', '-v', 'error']
    if a is not None:
        cmd += ['-ss', f'{max(a, 0):.3f}']
    if b is not None:
        cmd += ['-to', f'{b:.3f}']
    cmd += ['-i', path, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0

