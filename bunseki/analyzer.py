from pathlib import Path
import librosa

class Analyzer:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        
        allowed_suffixes = [".mp3", ".wav", ".flac", ".ogg"]

        if self.path.suffix not in allowed_suffixes:
            raise ValueError(f"Unsupported file format: {self.path.suffix} in {self.path}")

