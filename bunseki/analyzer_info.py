import librosa

class AnalysisInfo:
    def __init__(self, path) -> None:
        self.path = path

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
    def librosa_duration(self):
        return librosa.get_duration(path = self.path)