import os
import uuid
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import assemblyai as aai
import google.generativeai as genai

load_dotenv()

MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create folders
OUTPUT_DIR = "generated_audio"
TEMP_DIR = "temp_uploads"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


# In-memory chat history storage
# Structure: { session_id: [ {"role": "user"/"assistant", "content": "..."} ] }
chat_history = {}


# ----------------------
# Day 10: Chat History Endpoint
# ----------------------
@app.post("/agent/chat/{session_id}")
async def chat_with_history(session_id: str, file: UploadFile = File(...)):
    try:
        temp_filename = os.path.join(TEMP_DIR, f"input_{uuid.uuid4()}.wav")
        with open(temp_filename, "wb") as f:
            f.write(await file.read())
        aai.settings.api_key = ASSEMBLYAI_API_KEY
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_filename)

        if transcript.status != aai.TranscriptStatus.completed:
            return {"error": "Transcription failed"}
        user_text = transcript.text.strip()

        if session_id not in chat_history:
            chat_history[session_id] = []

        chat_history[session_id].append({"role": "user", "content": user_text})
        full_convo_text = ""
        for msg in chat_history[session_id]:
            prefix = "User: " if msg["role"] == "user" else "Assistant: "
            full_convo_text += prefix + msg["content"] + "\n"
        model = genai.GenerativeModel("gemini-2.5-pro")
        llm_response_text = model.generate_content(full_convo_text).text.strip()
        chat_history[session_id].append({"role": "assistant", "content": llm_response_text})
        chunks = []
        while len(llm_response_text) > 3000:
            split_point = llm_response_text.rfind(" ", 0, 3000)
            if split_point == -1:
                split_point = 3000
            chunks.append(llm_response_text[:split_point])
            llm_response_text = llm_response_text[split_point:].lstrip()
        chunks.append(llm_response_text)

        final_audio_parts = []
        for chunk in chunks:
            murf_url = "https://api.murf.ai/v1/speech/generate"
            headers = {
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "voiceId": "en-US-angela",
                "text": chunk,
                "format": "MP3",
                "sampleRate": 44100
            }
            r = requests.post(murf_url, headers=headers, json=payload)
            if r.status_code != 200:
                return {"error": f"Murf error: {r.text}"}
            audio_url = r.json().get("audioFile")
            audio_data = requests.get(audio_url)
            part_filename = os.path.join(OUTPUT_DIR, f"part_{uuid.uuid4()}.mp3")
            with open(part_filename, "wb") as out:
                out.write(audio_data.content)
            final_audio_parts.append(part_filename)

        final_output_file = os.path.join(OUTPUT_DIR, f"chat_{uuid.uuid4()}.mp3")
        with open(final_output_file, "wb") as outfile:
            for fname in final_audio_parts:
                with open(fname, "rb") as infile:
                    outfile.write(infile.read())

        return {
            "session_id": session_id,
            "transcript": user_text,
            "assistant_text": "".join(chunks),
            "audio_file": os.path.basename(final_output_file)
        }

    except Exception as error:
        return {"Error : Something went wrong, please try again later!!": str(error)}


# ----------------------
# File Serving
# ----------------------
@app.get("/files/{filename}")
def serve_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}