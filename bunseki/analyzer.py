from pathlib import Path
import librosa
import numpy as np
from bunseki.bunseki_colors import painted_string
import logging
from bunseki.audio_properties import AudioProperties
from bunseki.analyzer_info import AnalysisInfo

log = logging.getLogger("mahou.bunseki.analyzer")
logging.getLogger("numba").setLevel(logging.WARNING)

class Analyzer:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        
        if not self.path.is_file():
            raise IsADirectoryError(f"Invalid path, not a file: {self.path}")
        
        allowed_suffixes = [".mp3", ".wav", ".flac", ".ogg"]
        
        if self.path.suffix.lower() not in allowed_suffixes:
            raise ValueError(f"Unsupported file format: {self.path.suffix} in {self.path}")
        
        self.load_song(self.path)

        self.info = AnalysisInfo(self.path)
        # self.metrics = 
        self.properties = AudioProperties(self.audio, self.sample_rate)
        
        

    def load_song(self, path: Path):
        log.debug("Loading song...")
        self.audio, self.sample_rate = librosa.load(path, sr = None)
        log.debug("Loaded!")
        #Audio é a lista com todas as amostras
        #Sample rate é a frequencia de amostras de som em amostras/segundo


    @property
    def duration(self):
        #retorna o número de segundos da música
        seconds = len(self.audio) / self.sample_rate
        return seconds
    
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


    def see_all_info(self) -> str:
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
    


