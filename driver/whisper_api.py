import whisper
import numpy as np
import time
import sounddevice as sd


class WhisperRealTimeSpeechRecognizer:
    def __init__(self, success_func, error_func, close_func,
                 model: str = "base", silent_time: float = 0.7, silent_threshold: float = 0.02):
        self.success_func = success_func
        self.error_func = error_func
        self.close_func = close_func

        self.model = whisper.load_model(model)
        self.is_continue = True

        self.audio_buffer = []
        self.silence_threshold = silent_threshold
        self.silent_frames_required = int(silent_time * 16000)
        self.silent_frame_count = 0

    def closed(self):
        self.is_continue = False

    def statued(self):
        pass

    def callback(self, indata, frames, time, status):
        audio_data = indata.copy()
        audio_data = np.squeeze(audio_data)

        if np.max(np.abs(audio_data)) < self.silence_threshold:
            self.silent_frame_count += frames

        else:
            self.silent_frame_count = 0
            self.audio_buffer.append(audio_data)
        if self.silent_frame_count >= self.silent_frames_required:
            if len(self.audio_buffer) > 0:
                self.process_audio(np.concatenate(self.audio_buffer))
                self.audio_buffer = []

    def process_audio(self, audio_data):
        audio_data = whisper.pad_or_trim(audio_data)
        mel = whisper.log_mel_spectrogram(audio_data).to(self.model.device)
        options = whisper.DecodingOptions(language="zh", without_timestamps=True)
        result = whisper.decode(self.model, mel, options)
        self.success_func(result.text)

    def start_recognition(self):
        with sd.InputStream(callback=self.callback, channels=1, samplerate=16000):
            while self.is_continue:
                time.sleep(0.01)