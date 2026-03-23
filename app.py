import streamlit as st
import tempfile
import os
from groq import Groq
from pydub import AudioSegment
from pydub.utils import which

FFMPEG_PATH = r"C:\Users\chand\Downloads\ffmpeg_fullbuild\bin"
os.environ["PATH"] += os.pathsep + FFMPEG_PATH
AudioSegment.converter = which("ffmpeg") or os.path.join(FFMPEG_PATH, "ffmpeg.exe")
AudioSegment.ffprobe = which("ffprobe") or os.path.join(FFMPEG_PATH, "ffprobe.exe")

st.set_page_config(page_title="Audio → Transcript", layout="wide")
st.title("🎧 Audio → Transcript")
st.markdown("Upload audio → compress to MP3 → transcribe with Groq Whisper → download `.txt`")

GROQ_API_KEY = st.text_input("Groq API Key", type="password")


def compress_audio(input_path: str, output_path: str, target_kbps: int = 48):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="mp3", bitrate=f"{target_kbps}k")
    return output_path


def chunk_audio(audio_path: str, chunk_seconds: int = 60):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    step = chunk_seconds * 1000
    for i in range(0, len(audio), step):
        chunk_path = f"{audio_path}_chunk_{i}.wav"
        audio[i:i + step].export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def transcribe_chunks(chunks: list, model_name: str, api_key: str):
    client = Groq(api_key=api_key)
    texts = []
    for chunk in chunks:
        with open(chunk, "rb") as f:
            texts.append(client.audio.transcriptions.create(file=f, model=model_name).text)
    return "\n".join(texts)


uploaded = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a", "aac", "flac"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
        tf.write(uploaded.read())
        raw_path = tf.name

    st.audio(raw_path)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Compression")
        target_kbps = st.selectbox("Target bitrate (kbps)", [32, 48, 64], index=1)
    with col2:
        st.subheader("Whisper Model")
        model = st.selectbox("Model", ["whisper-large-v3-turbo", "whisper-large-v3"])
    with col3:
        st.subheader("Chunking")
        chunk_sec = st.slider("Chunk size (seconds)", 30, 300, 60)

    if st.button("Run"):
        if not GROQ_API_KEY:
            st.error("Enter Groq API Key")
        else:
            with st.spinner("Compressing → Chunking → Transcribing..."):
                base = os.path.splitext(raw_path)[0]
                fname = os.path.splitext(uploaded.name)[0]
                compressed_mp3 = base + "_compressed.mp3"

                compress_audio(raw_path, compressed_mp3, target_kbps)
                st.success(f"Compressed to {target_kbps} kbps MP3")
                st.audio(compressed_mp3)

                chunks = chunk_audio(compressed_mp3, chunk_sec)
                text = transcribe_chunks(chunks, model, GROQ_API_KEY)

                txt_path = base + "_transcript.txt"
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(text)

                st.subheader("Transcript")
                st.text_area("", text, height=400)

                with open(txt_path, "rb") as f:
                    st.download_button(
                        label="Download .txt",
                        data=f,
                        file_name=f"{fname}_transcript.txt",
                        mime="text/plain"
                    )

                st.success("Done")
