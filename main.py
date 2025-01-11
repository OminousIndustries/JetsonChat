# main.py

import threading
import time

# Local imports from our modules
from audio.vad import VADListener, load_silero_vad
from audio.stt import SileroSTT
from audio.tts import SileroTTS
from llm.ollama import OllamaClient
from face_animation.face import FaceAnimator

def main():
    # 1) Setup face animator in a separate thread
    face_animator = FaceAnimator(
        face_image_path="/home/omns/Desktop/Face2.png",
        mouth_image_path="/home/omns/Desktop/Jetson_Chat/assets/Mouth2.png",
        window_size=(800, 600),
        min_scale=1.0,
        max_scale=2.5
    )
    face_thread = threading.Thread(target=face_animator.run, daemon=True)
    face_thread.start()

    # 2) Load VAD
    print("-> Loading Silero VAD model...")
    vad_model = load_silero_vad()

    # 3) STT
    stt_model = SileroSTT(device="cpu")

    # 4) Ollama
    ollama_client = OllamaClient(url="http://localhost:11434/api/chat",
                                 model="llama3.2:1b",
                                 stream=True)

    # 5) TTS
    tts_model = SileroTTS(device="cpu", sample_rate=24000)

    # Callback when user finishes speaking
    def on_speech_detected(raw_bytes):
        # 1) Disable VAD while TTS is active to avoid picking up TTS output
        # Although TTS is playing on speakers, it might feed back into the mic
        # so let's disable temporarily
        vad_listener.disable_vad()

        # 2) STT
        recognized_text = stt_model.run_stt(raw_bytes, sample_rate=16000)
        print("-> User said:", recognized_text)

        # 3) If empty, re-enable VAD and return
        if not recognized_text.strip():
            vad_listener.enable_vad()
            return

        # 4) Query LLM
        llm_response = ollama_client.query(recognized_text)
        if not llm_response.strip():
            vad_listener.enable_vad()
            return

        # 5) Synthesize TTS
        audio_data = tts_model.synthesize(llm_response)

        # 6) Play TTS, providing amplitude updates to face_animator
        def amplitude_callback(ampl):
            face_animator.update_amplitude(ampl)

        tts_model.play_audio_with_amplitude(audio_data, amplitude_callback)

        # Once TTS finished, re-enable VAD
        vad_listener.enable_vad()

    # Create VADListener
    vad_listener = VADListener(
        sample_rate=16000,
        chunk_sec=0.5,
        speech_pause_sec=1.0,
        device_index=None,      # adjust if needed
        vad_device=vad_model,
        on_speech_callback=on_speech_detected
    )

    # 6) Start VAD in the main thread
    print("-> Starting the VAD listener...")
    try:
        vad_listener.start()  # Blocks indefinitely
    except KeyboardInterrupt:
        print("Shutting down...")
        vad_listener.stop()
        face_animator.stop()

if __name__ == "__main__":
    main()
