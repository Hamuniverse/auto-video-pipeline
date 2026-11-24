import subprocess
from pathlib import Path

BG_VIDEO = Path("assets/bg.mp4")
AUDIO_FILE = "output/voice.mp3"
SUBS_FILE = "output/subs.srt"
OUTPUT_VIDEO = "output/final.mp4"


def render_video():
    sub_style = (
        "FontName=Arial,FontSize=16,Alignment=2,MarginV=65,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2"
    )

    if BG_VIDEO.exists():
        input_args = ["-stream_loop", "-1", "-i", str(BG_VIDEO)]
        vf_filter = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,subtitles={SUBS_FILE}:force_style='{sub_style}'"
        )
    else:
        input_args = ["-f", "lavfi", "-i", "color=c=0x111827:s=1080x1920:r=30"]
        vf_filter = f"subtitles={SUBS_FILE}:force_style='{sub_style}'"

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-i", AUDIO_FILE,
        "-map", "0:v", "-map", "1:a",
        "-vf", vf_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest",
        OUTPUT_VIDEO,
    ]

    subprocess.run(cmd, check=True)
    print(f"Render selesai: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    render_video()