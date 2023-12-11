import os
import time
import requests
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from fpdf import FPDF
from tqdm import tqdm
import whisper
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

print(f"Current Working Directory: {os.getcwd()}")

# Replace the placeholder with the actual path to ffmpeg.exe
os.environ["PATH"] += os.pathsep + r'C:\Windows\System32'

def current_time():
    return time.time()

def elapsed_time(start_time):
    return time.time() - start_time

# Function to transcribe a segment file
def transcribe_segment(segment_path, index):
    print(f"Transcribing segment {index}...")

    # Load the Whisper model
    model = whisper.load_model("base")

    # Transcribe the audio directly from the file path
    result = model.transcribe(segment_path)
    print(f"\nFinished segment {index}.")
    return result["text"]

# Split the audio file into segments and save them
def split_audio(audio_path, segment_length=180000):  # 3 mins per segment
    print("Splitting audio into segments...")
    audio = AudioSegment.from_wav(audio_path)
    length = len(audio)
    segment_paths = []

    # Create the 'segments' directory if it doesn't exist
    segments_dir = "segments"
    if not os.path.exists(segments_dir):
        print("Creating 'segments' directory...")
        os.makedirs(segments_dir)
    else:
        print("'segments' directory already exists.")

    for i in range(0, length, segment_length):
        segment = audio[i:i + segment_length]
        segment_path = os.path.join(segments_dir, f"segment_{i//segment_length}.wav")
        segment.export(segment_path, format="wav")
        print(f"Segment saved: {segment_path}")
        segment_paths.append(segment_path)

    return segment_paths

# Main transcription function
def transcribe_audio(audio_path):
    segment_paths = split_audio(audio_path)
    transcriptions = []
    start_time = time.time()
    completed_segments = 0

    # Limit the number of threads to the total cores minus 2
    max_workers = max(1, multiprocessing.cpu_count() - 2)  # Ensure at least 1 worker

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(transcribe_segment, path, idx): idx for idx, path in enumerate(segment_paths)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Transcribing Segments"):
            transcription = future.result()
            transcriptions.append(transcription)
            completed_segments += 1

            # Calculate average time per segment and estimate remaining time
            avg_time_per_segment = (time.time() - start_time) / completed_segments
            remaining_segments = len(segment_paths) - completed_segments
            eta_seconds = avg_time_per_segment * remaining_segments

            # Convert ETA to minutes and seconds
            eta_minutes = int(eta_seconds // 60)
            eta_seconds_remainder = int(eta_seconds % 60)
            print(f"Completed: {completed_segments}/{len(segment_paths)} - ETA: {eta_minutes} minutes and {eta_seconds_remainder} seconds")

    return " ".join(transcriptions)

# Step 1: Download the Video
video_url = "https://d1vmz9r13e2j4x.cloudfront.net/legislature/480/50021194.mp4"
video_path = "downloaded_video.mp4"
audio_path = "extracted_audio.wav"

# Check if the video is already downloaded
if not os.path.exists(video_path):
    print("Starting video download...")
    start_time = current_time()

    response = requests.get(video_url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open(video_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

    print(f"Video downloaded. Time taken: {elapsed_time(start_time):.2f} seconds.")
else:
    print("Video already downloaded.")

# Step 2: Extract Audio from Video
if not os.path.exists(audio_path):
    print("Starting audio extraction...")
    start_time = current_time()

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

    print(f"Audio extracted. Time taken: {elapsed_time(start_time):.2f} seconds.")
else:
    print("Audio already extracted.")

# Step 3: Transcribe Audio Using OpenAI's Whisper with Multithreading
print("Starting audio transcription...")
start_time = current_time()

try:
    transcription = transcribe_audio(audio_path)
    print(f"Transcription completed. Time taken: {elapsed_time(start_time):.2f} seconds.")
except Exception as e:
    print(f"Error during transcription: {e}")
    exit(1)

# Step 4: Generate a PDF with the Transcription
print("Starting PDF generation...")
def save_transcription_to_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    textobject = c.beginText()
    textobject.setTextOrigin(inch, 11*inch)
    textobject.setFont("Times-Roman", 12)

    # Add the text to the PDF
    for line in text.split('\n'):
        textobject.textLine(line)
    
    c.drawText(textobject)
    c.save()

print("Starting PDF generation with UTF-8 support...")
try:
    save_transcription_to_pdf(transcription, "transcription_utf8.pdf")
    print(f"PDF generated and saved as 'transcription_utf8.pdf'. Time taken: {elapsed_time(start_time):.2f} seconds.")
except Exception as e:
    print(f"Error during UTF-8 PDF generation: {e}")
