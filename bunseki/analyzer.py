from pathlib import Path
import librosa
import numpy as np
from mahou_libs import COLORS, painted_string
import logging
from .audio_properties import AudioProperties
from .analyzer_info import AnalysisInfo

log = logging.getLogger("mahou.bunseki.analyzer")
logging.getLogger("numba").setLevel(logging.WARNING)


#region Main Methods
class Analyzer:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

        self.check_path_valid()
        
        self.info = AnalysisInfo(self.path)

        self.properties_loaded: bool = False

        log.debug("song analyzer initialized")
        
    def check_path_valid(self):
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        if not self.path.is_file():
            raise IsADirectoryError(f"Invalid path, not a file: {self.path}")
        
        allowed_suffixes = [".mp3", ".wav", ".flac", ".ogg"]
        
        if self.path.suffix.lower() not in allowed_suffixes:
            raise ValueError(f"Unsupported file format: {self.path.suffix} in {self.path}")
        
        log.debug("analyzer's path is valid!")


    def load_properties(self):
        self.properties = AudioProperties(self.path)
        if self.properties:
            self.properties_loaded = True
            log.debug("audio properties loaded")
#endregion
#region BASICS (no loading)
    @property
    def duration(self):
        return self.info.librosa_duration
    
    @property
    def base60_duration(self):
        seconds = self.duration
        minutes = int(seconds//60)
        display_seconds = int(seconds % 60)
        
        return (minutes, display_seconds)
    
    def show_list(self, list):
        for item in list:
            print(item)
    
    def freq_to_note(self, freq):
        if freq <= 0:
            return "N/A"
        a440 = 69
        delta = 12 * np.log2(freq/440)

        note_number = a440 + delta
        note_number = round(note_number)

        octave = (note_number // 12) - 1
        note = note_number % 12

        notes_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
        final_note = f"{notes_names[note]}{octave}"

        return final_note
        # 2**1/12 * (freq)

#endregion

    #region Needs Loading
 
    def see_all_info(self) -> str:
        if not self.properties_loaded:
            self.load_properties()

        basic_info = (
            f"BASIC INFO:"
            f"\nTitle: {self.info.title}"
            f"\nFormat:{self.info.file_format}"
            f"\nDuration: {self.base60_duration[0]}min, {self.base60_duration[1]:02d}s"
            f"\nPath: {self.info.file_path}"
            )
        
        more_info = (
            f"MORE INFO:"
            f"\nRMS volume: {self.properties.rms_volume_total}"
            f"\nPeak amplitude: {self.properties.peak_amplitude}"
            f"\nSample rate: {self.properties.sample_rate}Hz"
            f"\nAverage dBFS: {self.properties.rms_dbfs_amplitude}"
        )

        return f"{basic_info}\n\n{more_info}"


    def get_analysis_dictionary(self):
        if not self.properties_loaded:
            raise RuntimeError("self.properties has not been loaded yet!")
        dictionary = {
            "title": self.info.title,
            "path": str(self.info.file_path),
            "format": self.info.file_format,
            "duration_seconds": self.properties.duration,
            "duration_base60": self.properties.base60_duration,
            "peak_dbfs": self.properties.peak_dbfs         
        }
        return dictionary


