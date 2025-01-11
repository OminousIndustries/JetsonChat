# audio/vad.py
import pyaudio
import numpy as np
import time
import wave
from silero_vad import load_silero_vad, get_speech_timestamps

class VADListener:
    """
    Continuously captures short audio chunks, uses Silero VAD
    to detect speech segments, and calls a callback with
    the final speech audio once user stops talking.
    """
    def __init__(self,
                 sample_rate=16000,
                 chunk_sec=0.5,
                 speech_pause_sec=1.0,
                 device_index=None,
                 vad_device=None,
                 on_speech_callback=None):
        """
        sample_rate: STT sample rate (e.g. 16000)
        chunk_sec: length of each chunk in seconds (for VAD)
        speech_pause_sec: how long of silence after we last
                          detected speech to consider the utterance done
        device_index: optional PyAudio device index
        vad_device: loaded Silero VAD model
        on_speech_callback: function(audio_bytes) -> None
        """
        self.sample_rate = sample_rate
        self.chunk_sec = chunk_sec
        self.chunk_size = int(sample_rate * chunk_sec)
        self.speech_pause_sec = speech_pause_sec
        self.device_index = device_index
        self.vad_model = vad_device
        self.on_speech_callback = on_speech_callback

        self.pa = pyaudio.PyAudio()
        self.stream = None

        # This flag allows us to disable VAD if TTS is playing
        self.vad_enabled = True

        self._stop_flag = False

    def start(self):
        """Start audio capturing in an infinite loop (blocking)."""
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=1024
        )

        speech_active = False
        speech_buffer = []
        last_speech_time = time.time()

        print("-> VAD listening loop started.")
        while not self._stop_flag:
            # Read chunk
            audio_chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)

            if not self.vad_enabled:
                # If VAD is disabled, skip detection
                continue

            data_np = np.frombuffer(audio_chunk, np.int16).astype(np.float32) / 32768.0

            # Detect speech in this chunk
            speech_ts = get_speech_timestamps(data_np,
                                              self.vad_model,
                                              sampling_rate=self.sample_rate,
                                              return_seconds=False)
            if len(speech_ts) > 0:
                # We detected speech
                speech_buffer.append(audio_chunk)
                speech_active = True
                last_speech_time = time.time()
            else:
                # no speech in this chunk
                if speech_active:
                    if (time.time() - last_speech_time) > self.speech_pause_sec:
                        # speech ended
                        print("-> Speech ended, handing off to STT callback.")
                        all_audio = b''.join(speech_buffer)
                        speech_buffer.clear()
                        speech_active = False

                        # Fire callback
                        if self.on_speech_callback:
                            self.on_speech_callback(all_audio)

        # End loop
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def stop(self):
        self._stop_flag = True

    def enable_vad(self):
        self.vad_enabled = True

    def disable_vad(self):
        self.vad_enabled = False
