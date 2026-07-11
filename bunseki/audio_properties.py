import numpy as np
import logging
from mahou_libs import mahou_math

log = logging.getLogger("mahou.bunseki.analyzer.properties")
logging.getLogger("numba").setLevel(logging.WARNING)

class AudioProperties:
    def __init__(self, audio, sample_rate) -> None:
        self.audio = audio
        self.sample_rate = sample_rate
    
#region METRICS

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
    def rms_list(self):
        return self.slicer_rms_list_maker(self.audio, window_size = 512)
    
    
    def get_beats(self, window_size = 512):
        beats = []
        step = window_size // 2
        audio_rms = self.slicer_rms_list_maker(
            self.audio,
            window_size = window_size
        )

        rms_mean = np.mean(audio_rms)
        for i in range(1, len(audio_rms)-1):
            
            previous_rms = audio_rms[i-1]
            rms = audio_rms[i]
            next_rms = audio_rms[i+1]
            

            is_peak = ((rms > previous_rms) and (rms > next_rms))

            if is_peak:

                chunk_prominence = ((rms - previous_rms) + (rms - next_rms)) / 2
                surrounding_rms = mahou_math.mean(previous_rms, next_rms)

                is_significant_peak = (
                rms > 1.5 * rms_mean and
                chunk_prominence > 0.15*surrounding_rms and
                rms > 1.2 *surrounding_rms
                )

                if is_significant_peak:
                    time_in_seconds = (i*step) / self.sample_rate
                    beats.append((rms, time_in_seconds))

        
        filtered_beats = []
        for beat in beats:
            if not filtered_beats:
                filtered_beats.append(beat)
                continue

            previous_beat = filtered_beats[-1]
            time_difference = beat[1] - previous_beat[1]

            if time_difference < 0.15:
                if beat[0] > previous_beat[0]:
                    filtered_beats[-1] = beat

            else:
                filtered_beats.append(beat)
            

        return filtered_beats

    @property
    def estimated_bpm(self):

        beats_list = self.get_beats()

        if len(beats_list) < 2:
            return None

        differences = []
        for i in range(1, len(beats_list)):
            time_between_beats = beats_list[i][1] - beats_list[i-1][1] 
            differences.append(time_between_beats)
            
        return 60 / np.median(differences)

    
    @property
    def rms_dbfs_amplitude(self):
        if self.rms_volume_total == 0:
            return -np.inf

        return self.turn_into_dBFS(self.rms_volume_total)
    
    def turn_into_time(self, number):
        minutes = int(number // 60)
        seconds = number % 60
        return f"{minutes}:{seconds:05.2f}"
#endregion

    #region SPECTRUM

    @property
    def fourier_spectrum(self):
        return self.fourier(self.audio, window_size = 1024, top_n_freqs = 10)
    
    def fourier(self, audio, window_size, top_n_freqs):
        log.debug("Loading fourier list...")
        fourier_list: list = []
        freqs = np.fft.rfftfreq(window_size, d = 1/self.sample_rate)

        step = window_size // 2
        window = np.hanning(window_size)
        for eachslice in range(0, len(audio), step):
            window_index = eachslice // step

            time_in_seconds = (window_index * step) / self.sample_rate

            chunk = audio[eachslice:eachslice+window_size]
            if len(chunk) < window_size:
                continue

            
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
    

    #endregion
    