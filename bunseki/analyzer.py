from pathlib import Path
import librosa

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
        

    def load_song(self, path: Path):
        self.audio, self.sample_rate = librosa.load(path)

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
    def RMS_volume(self):
        amplitude = abs(self.audio)

        squared_amplitude = amplitude**2

        mean_squared_amplitude = squared_amplitude.mean()

        mean_amplitude = mean_squared_amplitude**(1/2)

        return mean_amplitude

    @property
    def desvio_padrão(self):
        amplitude = abs(self.audio)
        mean_amplitude = amplitude.mean()

        diff_squared_sum = 0

        for sample in self.audio:
            diff = sample - mean_amplitude
            diff_squared = diff**2
            diff_squared_sum += diff_squared
        
        variancia = diff_squared_sum/len(self.audio)

        return variancia**1/2

    
    def see_all_info(self) -> str:
        return (
            f"Title: {self.title}"
            f"\nFormat:{self.file_format}"
            f"\nDuration: {self.base60_duration[0]}min, {self.base60_duration[1]:02d}s"
            f"\nPath: {self.file_path}"

            f"\nRMS volume: {self.RMS_volume}"
            )
    


