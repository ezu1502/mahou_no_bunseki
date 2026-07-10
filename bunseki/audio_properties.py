import numpy as np
import logging

log = logging.getLogger("mahou.bunseki.analyzer.properties")
logging.getLogger("numba").setLevel(logging.WARNING)

class Properties:
    def __init__(self, audio, sample_rate) -> None:
        self.audio = audio
        self.sample_rate = sample_rate
    
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
    
    @property
    def get_rms_list(self):
        return self.slicer_rms_list_maker(self.audio, window_size = 512)
    
    @property
    def get_fourier_spectrum(self):
        return self.fourier(self.audio, window_size = 1024, top_n_freqs = 10)[:2]
    
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