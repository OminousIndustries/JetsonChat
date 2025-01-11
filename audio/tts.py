# audio/tts.py
import torch
import numpy as np
import pyaudio
import wave
import soundfile as sf

class SileroTTS:
    def __init__(self, device="cpu", sample_rate=24000):
        print("-> Loading Silero TTS model...")
        model_tts, example_text = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='en',
            speaker='v3_en'
        )
        model_tts.to(device)
        self.model = model_tts
        self.device = device
        self.sample_rate = sample_rate

    def synthesize(self, text):
        """
        Returns a float32 numpy array for the TTS audio.
        """
        if not text:
            return None
        print("-> Synthesizing TTS for:", text)
        audio = self.model.apply_tts(text=text,
                                     speaker='en_0',
                                     sample_rate=self.sample_rate)
        return audio

    def play_audio_with_amplitude(self, audio_data, amplitude_callback=None):
        """
        Plays the given float32 numpy array (single-channel).
        If amplitude_callback is provided, pass the amplitude
        of each chunk to it for mouth animation, etc.
        """
        if audio_data is None or len(audio_data) == 0:
            return
        
        # Check if it's a torch Tensor
        if torch.is_tensor(audio_data):
            # Move to CPU if needed, convert to NumPy
            audio_data = audio_data.cpu().numpy()  
            # Now it's a NumPy array, e.g. float32 in [-1..1]

        pa = pyaudio.PyAudio()

        # Convert float32 [-1..1] to int16
        audio_int16 = np.clip(audio_data * 32767.0, -32767.0, 32767.0).astype(np.int16)
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=self.sample_rate,
                         output=True)

        chunk_size = 1024
        idx = 0
        total_frames = len(audio_int16)

        while idx < total_frames:
            chunk_end = min(idx + chunk_size, total_frames)
            chunk = audio_int16[idx:chunk_end]
            stream.write(chunk.tobytes())

            if amplitude_callback:
                # amplitude = mean absolute value
                amplitude = np.abs(chunk.astype(np.float32)).mean()
                amplitude_callback(amplitude)

            idx += chunk_size

        stream.stop_stream()
        stream.close()
        pa.terminate()
