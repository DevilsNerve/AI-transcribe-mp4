---

# Audio to Text Transcription Tool

## Overview
This tool is designed to automate the process of converting audio from a video into a text transcription. It downloads a video, extracts the audio, splits the audio into manageable segments, transcribes each segment using OpenAI's Whisper model, and compiles the transcriptions into a single PDF file.

## Requirements
- Python 3.x
- `requests`
- `pydub`
- `moviepy`
- `FPDF`
- `tqdm`
- `whisper`
- `concurrent.futures`
- `multiprocessing`
- `reportlab`

## Installation
Before running the script, ensure you have Python installed on your machine and then install the required packages using pip:

```bash
pip install requests pydub moviepy fpdf tqdm whisper reportlab
```

## Usage
To use the tool, follow these steps:
1. Ensure `ffmpeg.exe` is accessible in your system's PATH.
2. Modify the `video_url` variable in the script to point to the video you want to transcribe.
3. Run the script using Python.

## Example
Here's an example of how to run the script:

```bash
python transcription_tool.py
```

The script performs the following steps:
1. Downloads the video from the specified URL.
2. Extracts the audio from the downloaded video.
3. Splits the audio into segments and saves them in a directory.
4. Transcribes each audio segment using Whisper and saves the transcriptions.
5. Compiles all transcriptions into a PDF file.

## Notes
- The script uses OpenAI's Whisper model for transcription, which requires a good internet connection for model downloading.
- The script currently saves the transcribed segments in a folder named 'transcriptions'.

---
