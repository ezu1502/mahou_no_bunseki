import numpy as np
import logging
from mahou_libs.mahou_math import statistic
from pathlib import Path
from functools import wraps
import soundfile as sf

log = logging.getLogger("mahou.bunseki.analyzer.properties")
logging.getLogger("numba").setLevel(logging.WARNING)


def check_audio_exists(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if self.audio:
                return function(*args, **kwargs)
            else:
                raise RuntimeError("self.audio does not exist!!")
        return wrapper

class AudioProperties:
    def __init__(self, path) -> None:
        self.path = path
        self.audio = None
        self.sample_rate = None
        self.load_song(path)
    

    def load_song(self, path: Path):
        if self.audio is None:
            log.debug("Loading song...")
            self.audio, self.sample_rate = sf.read(path, dtype = "float32")
            log.debug("Loaded! -> self.audio and self.sample created")

        #Audio é a lista com todas as amostras
        #Sample rate é a frequencia de amostras de som em amostras/segundo

#region METRICS

    @property
    def duration(self):
        if self.audio is None or self.sample_rate is None:
            return
        #retorna o número de segundos da música
        seconds = len(self.audio) / self.sample_rate
        return seconds
    
    @property
    def base60_duration(self):
        if self.duration is None:
            return
        
        seconds = self.duration
        minutes = int(seconds//60)
        display_seconds = int(seconds % 60)
        
        return (minutes, display_seconds)
    
    @property
    def peak_amplitude(self):
        if self.audio is None or self.sample_rate is None:
            return
        peak = np.max(np.abs(self.audio))
        if peak > 1:
            log.info(f"Peak amplitude is greater than 1: {peak}")
        return peak
    
    @property
    def peak_dbfs(self):
        return self.turn_into_dBFS(self.peak_amplitude)
    
    def turn_into_dBFS(self, amplitude):
        if amplitude <= 0:
            return -np.inf
        return 20 * np.log10(amplitude)

    @property
    def rms_volume_total(self):
        amplitude = self.audio

        return self.get_rms(amplitude)


    def get_rms(self, sample_list):
        amplitude = np.abs(sample_list)

        squared_amplitude = amplitude**2

        mean_squared_amplitude = squared_amplitude.mean()

        mean_amplitude = mean_squared_amplitude**(1/2)

        return mean_amplitude

    def slicer_rms_list_maker(self, audio, window_size = 512):
        #window_size é o tamanho da janela de cada amostra
        rms_list: list = []
        step = window_size // 2
        for i in range(0, len(audio), step):
            chunk = audio[i:i+window_size]

            if len(chunk) < window_size:
                continue
            chunk_rms = self.get_rms(chunk)
            rms_list.append(chunk_rms)
        return rms_list
    
    @property
    def rms_dbfs_amplitude(self):
        if self.rms_volume_total == 0:
            return -np.inf

        return self.turn_into_dBFS(self.rms_volume_total)
    
    def turn_into_time(self, number):
        minutes = int(number // 60)
        seconds = number % 60
        return f"{minutes}:{seconds:05.2f}"

    @property
    def rms_list(self):
        return self.slicer_rms_list_maker(self.audio, window_size = 512)
    
    
    @property
    def estimated_bpm(self):
        # beats_list = self.get_beats()

        # if beats_list is None:
        #     return

        # if len(beats_list) < 2:
        #     return None

        # differences = []
        # for i in range(1, len(beats_list)):
        #     time_between_beats = beats_list[i][1] - beats_list[i-1][1] 
        #     differences.append(time_between_beats)
            
        # return 60 / np.median(differences)
        # ? Precisa de um algoritmo de reconhecimento de batidas  ainda
        return None

    
    
#endregion

    #region SPECTRUM


    #endregion
    