from pathlib import Path
import librosa
import numpy as np
from bunseki.bunseki_colors import painted_string
import logging
from bunseki.audio_properties import Properties

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

        self.properties = Properties(self.audio, self.sample_rate)
        

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
    
    @property
    def file_path(self):
        return self.path
    
    @property
    def title(self):
        return self.path.stem
    
    @property
    def file_format(self):
        return self.path.suffix.lower()
    
    @property
    def peak_amplitude(self):
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
        amplitude = np.abs(self.audio)

        squared_amplitude = amplitude**2

        mean_squared_amplitude = squared_amplitude.mean()

        mean_amplitude = mean_squared_amplitude**(1/2)

        return mean_amplitude

    @property
    def get_rms_list(self):
        return self.slicer_rms_list_maker(self.audio, window_size = 512)
    
    @property
    def get_fourier_spectrum(self):
        return self.fourier(self.audio, window_size = 1024, top_n_freqs = 10)[:2]
                
    @property
    def standard_deviation(self):
        amplitude = self.audio
        mean_amplitude = amplitude.mean()

        diff_squared_sum = 0

        for sample in self.audio:
            diff = sample - mean_amplitude
            diff_squared = diff**2
            diff_squared_sum += diff_squared
        
        variancia = diff_squared_sum/len(self.audio)

        return variancia**(1/2) 
    
    @property
    def rms_dbfs_amplitude(self):
        if self.rms_volume_total == 0:
            return -np.inf

        return self.turn_into_dBFS(self.rms_volume_total)
    
    def slicer_rms_list_maker(self, audio, window_size = 512):
        #window_size é o tamanho da janela de cada amostra
        rms_list: list = []
        step = window_size // 2
        for i in range(0, len(audio), step):
            chunk = audio[i:i+window_size]
            chunk_squared = chunk ** 2
            chunk_squared_mean = np.mean(chunk_squared) 
            chunk_rms = np.sqrt(chunk_squared_mean)
            rms_list.append(chunk_rms)
        return rms_list
        


    
    def fourier(self, audio, window_size, top_n_freqs):
        log.debug("Loading fourier list...")
        fourier_list: list = []
        freqs = np.fft.rfftfreq(window_size, d = 1/self.sample_rate)

        step = window_size // 2
        for eachslice in range(0, len(audio), step):
            window_index = eachslice // step

            time_in_seconds = (window_index * step) / self.sample_rate

            chunk = audio[eachslice:eachslice+window_size]
            if len(chunk) < window_size:
                continue

            window = np.hanning(window_size)
            windowed_chunk = chunk * window

            result = np.fft.rfft(windowed_chunk)
            magnitudes = np.abs(result)
            magnitudes[0] = 0
            top_indexes = np.argsort(magnitudes)[-top_n_freqs:][::-1]

            for index in top_indexes:
                if magnitudes[index] < 1e-6:
                    continue
                fourier_list.append((self.turn_into_time(time_in_seconds), freqs[index], magnitudes[index]))
        return fourier_list
    
    def turn_into_time(self, number):
        minutes = int(number // 60)
        seconds = number % 60
        return f"{minutes}:{seconds:05.2f}"


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
            f"\nTitle: {self.title}"
            f"\nFormat:{self.file_format}"
            f"\nDuration: {self.base60_duration[0]}min, {self.base60_duration[1]:02d}s"
            f"\nPath: {self.file_path}"
            )
        
        more_info = (
            f"MORE INFO:"
            f"\nRMS volume: {self.rms_volume_total}"
            f"\nPeak amplitude: {self.peak_amplitude}"
            f"\nSample rate: {self.sample_rate}Hz"
            f"\nAverage dBFS: {self.rms_dbfs_amplitude}"
        )

        return f"{basic_info}\n\n{more_info}"
    


