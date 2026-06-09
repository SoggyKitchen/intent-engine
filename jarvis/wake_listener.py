"""
jarvis/wake_listener.py
───────────────────────
Always-on voice assistant for SaaSpare. Say "Hey Jarvis" and ask anything.

SETUP (run once):
    pip install pvporcupine pvrecorder openai-whisper pyttsx3

FREE Porcupine access key: https://console.picovoice.ai/ (free tier, no credit card)
Set it as env var:  PORCUPINE_KEY=your_key_here
Or put it in jarvis/.env:  PORCUPINE_KEY=your_key_here

RUN:
    uv run python jarvis/wake_listener.py

USAGE:
    Say "Hey Jarvis" → wait for beep → speak your command
    "Hey Jarvis, how's the company?"
    "Hey Jarvis, what are the top revenue opportunities?"
    "Hey Jarvis, run the daily brief"
    "Hey Jarvis, what did we deploy recently?"
"""

import os
import sys
import subprocess
import tempfile
import threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

# ── load .env if present ──────────────────────────────────────────────────────
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

PORCUPINE_KEY = os.environ.get("PORCUPINE_KEY", "")

# ── TTS ───────────────────────────────────────────────────────────────────────

def speak(text: str):
    """Speak via pyttsx3 or PowerShell SAPI fallback."""
    print(f"\n[JARVIS] {text}\n")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        for v in engine.getProperty("voices"):
            if "david" in v.name.lower() or "mark" in v.name.lower():
                engine.setProperty("voice", v.id)
                break
        engine.say(text)
        engine.runAndWait()
    except Exception:
        safe = text.replace("'", "").replace('"', "")[:1500]
        subprocess.run(
            ["powershell", "-Command",
             f"Add-Type -AssemblyName System.Speech; "
             f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
             f"$s.Rate = 2; $s.Speak('{safe}')"],
            check=False
        )

# ── STT ───────────────────────────────────────────────────────────────────────

def transcribe(audio_path: str) -> str:
    """Transcribe audio file using local Whisper (offline, private)."""
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"].strip()
    except ImportError:
        speak("Whisper not installed. Run: pip install openai-whisper")
        return ""
    except Exception as e:
        speak(f"Transcription error: {e}")
        return ""

# ── Claude brain ──────────────────────────────────────────────────────────────

JARVIS_SYSTEM = """You are JARVIS — the autonomous CEO brain of SaaSpare.org.
You speak like JARVIS from Iron Man: sharp, British-dry, efficient.
Address the user as "sir" or "Kaylan". Keep spoken replies under 4 sentences —
they'll be read aloud. For data questions, pull from seo/reports/ files.
For business questions, check MEMORY.md and CLAUDE.md.
Never invent affiliate links, pricing figures, or earnings data.
If asked to make a change, confirm before acting.
"""

def ask_jarvis(command: str) -> str:
    """Pass command to Claude CLI and get response."""
    prompt = f"{JARVIS_SYSTEM}\n\nUser command: {command}"
    try:
        result = subprocess.run(
            ["claude", "-p", prompt,
             "--allowedTools", "Read,Bash",
             "--max-turns", "3"],
            capture_output=True, text=True, cwd=ROOT, timeout=60
        )
        response = result.stdout.strip()
        if not response:
            response = result.stderr.strip()
        # Keep it speakable — first 400 chars if long
        if len(response) > 400:
            response = response[:397] + "..."
        return response or "I was unable to process that request, sir."
    except subprocess.TimeoutExpired:
        return "The request timed out, sir. Try a simpler command."
    except FileNotFoundError:
        return "Claude CLI not found. Ensure 'claude' is in your PATH."
    except Exception as e:
        return f"Error: {e}"

# ── audio recording ───────────────────────────────────────────────────────────

def record_until_silence(max_seconds: int = 8, silence_threshold: float = 0.01) -> str:
    """Record audio until silence or max_seconds. Returns temp file path."""
    try:
        import sounddevice as sd
        import numpy as np
        import wave

        sample_rate = 16000
        frames = []
        silence_frames = 0
        silence_limit = int(sample_rate * 1.5 / 1024)  # 1.5s silence

        print("[JARVIS] Listening...")

        with sd.InputStream(samplerate=sample_rate, channels=1,
                            dtype="int16", blocksize=1024) as stream:
            for _ in range(int(sample_rate * max_seconds / 1024)):
                data, _ = stream.read(1024)
                frames.append(data.copy())
                rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))
                if rms < silence_threshold * 32768:
                    silence_frames += 1
                    if silence_frames > silence_limit and len(frames) > 10:
                        break
                else:
                    silence_frames = 0

        tmp = tempfile.mktemp(suffix=".wav")
        with wave.open(tmp, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            import numpy as np
            wf.writeframes(np.concatenate(frames).tobytes())
        return tmp

    except ImportError:
        speak("sounddevice not installed. Run: pip install sounddevice numpy")
        return ""
    except Exception as e:
        speak(f"Recording error: {e}")
        return ""

# ── main wake-word loop ───────────────────────────────────────────────────────

def run_with_porcupine():
    """Full wake-word loop using Picovoice Porcupine."""
    if not PORCUPINE_KEY:
        print("[JARVIS] No PORCUPINE_KEY found.")
        print("  Get a free key at https://console.picovoice.ai/")
        print("  Add it to jarvis/.env as: PORCUPINE_KEY=your_key_here")
        print("  Running in text-input mode instead...\n")
        run_text_mode()
        return

    try:
        import pvporcupine
        from pvrecorder import PvRecorder

        porcupine = pvporcupine.create(
            access_key=PORCUPINE_KEY,
            keywords=["jarvis"]  # Built-in wake word
        )
        recorder = PvRecorder(device_index=-1,
                              frame_length=porcupine.frame_length)

        speak("SaaSpare Jarvis online. Say 'Hey Jarvis' to activate.")
        recorder.start()

        print("\n[JARVIS] Listening for wake word 'Jarvis'...")
        print("[JARVIS] Press Ctrl+C to stop.\n")

        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)
            if result >= 0:
                recorder.stop()
                speak("Yes, sir?")

                audio_file = record_until_silence()
                if audio_file:
                    command = transcribe(audio_file)
                    Path(audio_file).unlink(missing_ok=True)
                    if command:
                        print(f"[YOU] {command}")
                        response = ask_jarvis(command)
                        speak(response)

                recorder.start()

    except ImportError:
        print("\n[JARVIS] Porcupine not installed.")
        print("  Run: pip install pvporcupine pvrecorder")
        print("  Falling back to text mode...\n")
        run_text_mode()
    except KeyboardInterrupt:
        speak("Signing off, sir. Good day.")
    finally:
        try:
            recorder.delete()
            porcupine.delete()
        except Exception:
            pass

def run_text_mode():
    """Fallback: type commands instead of speaking."""
    speak("Running in text mode. Type your commands.")
    print("\n[JARVIS TEXT MODE] Type commands. 'quit' to exit.\n")
    while True:
        try:
            command = input("You: ").strip()
            if command.lower() in ("quit", "exit", "bye"):
                speak("Signing off, sir.")
                break
            if command:
                response = ask_jarvis(command)
                speak(response)
        except (KeyboardInterrupt, EOFError):
            speak("Signing off, sir.")
            break

# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--text" in sys.argv:
        run_text_mode()
    else:
        run_with_porcupine()
