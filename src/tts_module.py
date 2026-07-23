import threading
import pyttsx3
from src.logger import logger


class TTSManager:
    """Asynchronous Text-to-Speech Manager to prevent execution blocking."""

    def __init__(self):
        self._lock = threading.Lock()

    def _speak_worker(self, text: str):
        with self._lock:
            try:
                engine = pyttsx3.init()
                rate = engine.getProperty("rate")
                engine.setProperty("rate", rate - 20)  # slightly slower for clarity

                # Force English voice selection
                voices = engine.getProperty("voices")
                english_voice = None
                for voice in voices:
                    v_name = (voice.name or "").lower()
                    v_id = (voice.id or "").lower()
                    v_langs = [str(l).lower() for l in getattr(voice, 'languages', [])]
                    if any(tag in v_id or tag in v_name for tag in ["en-us", "en_us", "en-gb", "en_gb", "david", "zira", "mark", "hazel", "george", "english"]):
                        english_voice = voice.id
                        break
                    if any("en" in l for l in v_langs):
                        english_voice = voice.id
                        break

                if english_voice:
                    engine.setProperty("voice", english_voice)
                elif voices:
                    for voice in voices:
                        v_str = ((voice.id or "") + " " + (voice.name or "")).lower()
                        if "en" in v_str or "us" in v_str:
                            engine.setProperty("voice", voice.id)
                            break

                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS Engine failed: {e}")

    def speak_async(self, text: str):
        """Spawns a daemon thread to speak text immediately without blocking."""
        if not text:
            return
        logger.info(f"[TTS] Speaking: '{text}'")
        thread = threading.Thread(target=self._speak_worker, args=(text,), daemon=True)
        thread.start()


tts_manager = TTSManager()
