# 🎙 AI Voice Agent  
*(30 Days of AI Voice Agents - Day 13)*

An interactive **voice-based conversational AI agent** that records your speech, transcribes it to text, generates intelligent and context-aware replies using **Google Gemini**, and responds back using **Murf AI’s Text-to-Speech** — all while **maintaining chat history** for each session.

---

## 🚀 Features

- **🎤 Speech Recording** – Record your voice directly from the browser.
- **📝 Speech-to-Text** – Accurate transcription using **AssemblyAI**.
- **🤖 AI Conversation** – Context-aware replies via **Gemini 2.5 Pro**.
- **🔊 Text-to-Speech** – Lifelike audio responses from **Murf AI**.
- **💬 Chat History** – Keeps conversation context across multiple turns.
- **🌐 Cross-Origin Friendly** – Fully CORS-enabled for development.

---

## 🏗 Architecture

```
🎙 User Voice
     ↓
🌐 Frontend (HTML, CSS, JS, Bootstrap, Animate.css)
     ↓
🎧 Audio Capture (MediaRecorder API)
     ↓
🚀 FastAPI Backend
     ├─ Transcription via AssemblyAI
     ├─ Context-aware replies via Gemini
     ├─ Voice synthesis via Murf AI
     └─ Chat history stored in memory
     ↓
🔊 Play Audio + Show Transcript + Chat History
```
---

## 🛠 Technologies Used

### Frontend
- HTML5 / CSS3 / JavaScript (Vanilla)
- [Bootstrap 5](https://getbootstrap.com/)
- [Animate.css](https://animate.style/)

### Backend
- [FastAPI](https://fastapi.tiangolo.com/)
- [AssemblyAI](https://www.assemblyai.com/) – Speech-to-Text
- [Google Gemini](https://ai.google.dev/) – LLM
- [Murf AI](https://murf.ai/) – Text-to-Speech
- `python-dotenv` – Environment variable management
- `requests` – API calls
- `uuid` – Unique file/session IDs

---

## ⚙️ Environment Variables

Before running the app, create a `.env` file in the root directory:

```
MURF_API_KEY=your_murf_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ▶️ How to Run

###  Install Dependencies
```bash
pip install fastapi uvicorn python-dotenv requests assemblyai google-generativeai
```

###  Set Environment Variables
Create `.env` as described above.

###  Run FastAPI Server
```bash
uvicorn main:app --reload
```
The server will start at:  
`http://127.0.0.1:8000`

### Open Frontend
Open `index.html` in your browser.  
Ensure backend URLs in the script match your FastAPI server.

---

## 📂 Project Structure

```
.
├── main.py              # FastAPI backend
├── index.html           # Frontend UI
├── generated_audio/     # Stores generated MP3 files
├── temp_uploads/        # Temporary audio uploads
├── .env                 # API keys
└── README.md            # Documentation
```

## 💡 Notes

- Chat history is stored **in-memory** — it resets on server restart.
- API calls depend on valid keys; ensure `.env` is properly set.
- Audio responses may be split into chunks and concatenated for playback.

---

**💬 “Your voice, amplified by AI.”**
