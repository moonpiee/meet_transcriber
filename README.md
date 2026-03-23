# Meeting Transcriber (Audio to Transcripts)

A Streamlit app that compresses audio files and transcribes them using Groq's Whisper API.

---

## Features

- Accepts MP3, WAV, M4A, AAC, FLAC uploads
- Compresses audio to mono 16kHz MP3 (32–64 kbps)
- Splits audio into configurable chunks to stay within API limits
- Transcribes via Groq Whisper (`whisper-large-v3-turbo` or `whisper-large-v3`)
- Outputs a downloadable `.txt` transcript

---

## Pipeline Overview

```mermaid
flowchart LR
    A[Upload Audio\nmp3 / wav / m4a / aac / flac] --> B[Compress\nMono · 16kHz · low bitrate MP3]
    B --> C[Chunk\nconfigurable window in seconds]
    C --> D[Transcribe\nGroq Whisper API]
    D --> E[Download\n.txt transcript]
```

---

## Architecture

```mermaid
flowchart TD
    subgraph UI["Streamlit UI"]
        U1[File Uploader]
        U2[API Key Input]
        U3[Controls\nbitrate · model · chunk size]
        U4[Run Button]
        U5[Transcript Display]
        U6[Download Button]
    end

    subgraph Processing["Backend Processing"]
        P1[compress_audio\nAudioSegment → mono → 16kHz → MP3]
        P2[chunk_audio\nSplit into N-second WAV chunks]
        P3[transcribe_chunks\nGroq client loop over chunks]
    end

    subgraph External["External"]
        E1[FFmpeg\nCodec engine]
        E2[Groq API\nWhisper model]
    end

    U1 --> P1
    U4 --> P1
    P1 --> E1
    E1 --> P1
    P1 --> P2
    P2 --> P3
    P3 --> E2
    E2 --> P3
    P3 --> U5
    U5 --> U6
```

---

## Data Flow

```mermaid
sequenceDiagram
    actor User
    participant App as Streamlit App
    participant FFmpeg
    participant Groq as Groq Whisper API

    User->>App: Upload audio file
    User->>App: Set bitrate, model, chunk size
    User->>App: Click Run

    App->>FFmpeg: Compress → mono, 16kHz, N kbps MP3
    FFmpeg-->>App: Compressed MP3

    loop For each chunk
        App->>App: Slice chunk (WAV)
        App->>Groq: POST audio chunk
        Groq-->>App: Transcription text
    end

    App->>App: Join all chunk texts
    App-->>User: Display transcript
    App-->>User: Download .txt
```

---

## Setup

### Prerequisites

- Python 3.9+
- FFmpeg installed and accessible

#### Windows

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and update `FFMPEG_PATH` in `app.py`:
   ```python
   FFMPEG_PATH = r"C:\path\to\ffmpeg\bin"
   ```

#### macOS / Linux

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

Remove the manual `FFMPEG_PATH` block from `app.py` — FFmpeg will be found automatically via `PATH`.

---

### Install & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Configuration

| Control | Options | Default | Effect |
|---|---|---|---|
| Target bitrate | 32 / 48 / 64 kbps | 48 kbps | Lower = smaller file, slightly lower quality |
| Whisper model | `whisper-large-v3-turbo` / `whisper-large-v3` | turbo | Turbo is faster; v3 is more accurate |
| Chunk size | 30 – 300 seconds | 60 s | Smaller chunks = more API calls but safer for long files |

---

## Compression Strategy

```mermaid
flowchart LR
    A[Original Audio\nstereo · any sample rate · any format]
    --> B[Downmix to Mono\nhalves file size]
    --> C[Resample to 16kHz\noptimal for speech]
    --> D[MP3 Encode\n32–64 kbps]
    --> E[Compressed File\n~4–8× smaller]
```

Speech intelligibility is preserved at 16kHz mono because human voice sits well below 8kHz. The low bitrate MP3 encoding is sufficient for Whisper's input requirements.

---

## File Structure

```
.
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `groq` | Groq API client |
| `pydub` | Audio processing and chunking |
| `ffmpeg-python` | FFmpeg bindings (codec backend for pydub) |

---

## API Key

Get a free Groq API key at [console.groq.com](https://console.groq.com). Enter it in the app's text field — it is not stored anywhere.
