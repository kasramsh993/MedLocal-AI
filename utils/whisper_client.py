import os
import shutil
import tempfile
from pathlib import Path

import streamlit as st


def _ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg"):
        return

    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe",
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Microsoft"
        / "WinGet"
        / "Packages"
        / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
        / "ffmpeg-8.1.1-full_build"
        / "bin"
        / "ffmpeg.exe",
        Path(os.environ.get("ProgramFiles", "")) / "ffmpeg" / "bin" / "ffmpeg.exe",
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            os.environ["PATH"] = f"{candidate.parent}{os.pathsep}{os.environ.get('PATH', '')}"
            return

    raise FileNotFoundError(
        "ffmpeg was not found. Please install ffmpeg or add ffmpeg.exe to PATH before recording audio."
    )


@st.cache_resource(show_spinner=False)
def load_whisper_model(size: str):
    _ensure_ffmpeg_available()
    import whisper

    return whisper.load_model(size)


def transcribe_audio(audio_bytes: bytes, model_size: str) -> str:
    _ensure_ffmpeg_available()
    model = load_whisper_model(model_size)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = Path(f.name)
    try:
        result = model.transcribe(str(tmp_path), language="de", task="transcribe")
        return result["text"].strip()
    finally:
        tmp_path.unlink(missing_ok=True)
