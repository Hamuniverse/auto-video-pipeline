import subprocess
import sys

# Opsi suara lain: "id-ID-GadisNeural" (ID wanita), "en-US-AndrewNeural" (EN pria)
VOICE = "id-ID-ArdiNeural"


def generate_audio_and_subs():
    cmd = [
        sys.executable, "-m", "edge_tts",
        "--voice", VOICE,
        "--file", "output/narration.txt",
        "--write-media", "output/voice.mp3",
        "--write-subtitles", "output/subs.srt",
    ]
    subprocess.run(cmd, check=True)
    print("Audio (output/voice.mp3) dan subtitle (output/subs.srt) berhasil dibuat.")


if __name__ == "__main__":
    generate_audio_and_subs()