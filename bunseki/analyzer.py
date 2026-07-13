from pathlib import Path
import numpy as np
from mahou_libs import COLORS, painted_string
from mahou_libs.time_functions import log_delta_time
import logging
from .audio_properties import AudioProperties
from mutagen import File
import time

log = logging.getLogger("mahou.bunseki.analyzer")
logging.getLogger("numba").setLevel(logging.WARNING)


#region Main Methods
class Analyzer:
    @log_delta_time
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.check_path_valid()
        self.properties = None
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

    @log_delta_time
    def load_heavy_analysis(self):
        self.properties = AudioProperties(self.path)
        if self.properties:
            log.debug("audio properties loaded")
        else:
            log.warning("Heavy analysis loading failed")
    
#endregion
#region BASICS (no loading)
    @property
    def title(self):
        return self.path.stem
    @property
    def duration(self) -> int:
        audio_file = File(self.path)
        if audio_file is None or audio_file.info is None:
            raise ValueError("audio_file could not be read")
        
        return audio_file.info.length
    
    @property
    def base60_duration(self):
        seconds = self.duration
        minutes = int(seconds//60)
        display_seconds = int(seconds % 60)
        
        return (minutes, display_seconds)
    
    @property
    def base60_duration_str(self) -> str:
        seconds = self.duration
        minutes = int(seconds//60)
        display_seconds = int(seconds % 60)
        
        return f"{minutes}:{display_seconds:02d}"
    
    @property
    def file_format(self):
        return self.path.suffix.lower()
    
   

#endregion
#region non-property funcs
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
        if self.properties is None:
            self.load_heavy_analysis()
        
        if self.properties is not None:
            basic_info = (
                f"BASIC INFO:"
                f"\nTitle: {self.title}"
                f"\nFormat:{self.file_format}"
                f"\nDuration: {self.base60_duration[0]}min, {self.base60_duration[1]:02d}s"
                f"\nPath: {self.path}"
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
        dictionary = {
            "title": self.title,
            "path": str(self.path),
            "format": self.file_format,
            "duration_seconds": self.duration,
            "duration_base60": self.base60_duration
            }    
        if self.properties is not None:
            dictionary["peak_dbfs"] = self.properties.peak_dbfs 
        else:
            log.info("For more info, run load_heavy_analysis!")
        
        return dictionary




