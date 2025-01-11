# audio/stt.py
import torch
import wave
import os

class SileroSTT:
    def __init__(self, device="cpu"):
        print("-> Loading Silero STT model...")
        model_stt, decoder, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_stt',
            language='en',
            device=device
        )
        (read_batch, split_into_batches, read_audio, prepare_model_input) = utils

        self.model = model_stt
        self.decoder = decoder
        self.read_audio = read_audio
        self.prepare_model_input = prepare_model_input
        self.device = device

    def run_stt(self, raw_bytes, sample_rate=16000, temp_wav="temp_stt.wav"):
        """
        Writes raw PCM bytes to a temp WAV, runs Silero STT, returns text.
        """
        # Save to disk
        with wave.open(temp_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(raw_bytes)

        audio_tensor = self.read_audio(temp_wav)
        input_data = self.prepare_model_input([audio_tensor], device=self.device)
        output = self.model(input_data)
        text = self.decoder(output[0])
        # Optionally remove the temp file
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

        return text.strip()
