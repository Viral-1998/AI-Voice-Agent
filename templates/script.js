const API_BASE_URL = "http://localhost:8000";

let mediaRecorder;
let audioChunks = [];
const sessionId = crypto.randomUUID();

const recordBtn = document.getElementById("recordBtn");
const statusEl = document.getElementById("status");
const loadingEl = document.getElementById("loading");
const resultsEl = document.getElementById("results");
const transcriptText = document.getElementById("transcriptText");
const assistantText = document.getElementById("assistantText");
const audioPlayer = document.getElementById("audioPlayer");
const chatHistoryEl = document.getElementById("chatHistory");
const chatMessagesEl = document.getElementById("chatMessages");

recordBtn.addEventListener("click", () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    startRecording();
  } else {
    stopRecording();
  }
});

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = sendAudioToServer;

    mediaRecorder.start();
    recordBtn.textContent = "⏹ Stop Recording";
    statusEl.textContent = "Recording... 🎤";
  } catch (err) {
    console.error("Error accessing microphone", err);
    alert("Microphone access denied or not available.");
  }
}

function stopRecording() {
  mediaRecorder.stop();
  recordBtn.textContent = "🎤 Start Recording";
  statusEl.textContent = "";
}

async function sendAudioToServer() {
  const blob = new Blob(audioChunks, { type: "audio/wav" });
  const formData = new FormData();
  formData.append("file", blob, "recording.wav");

  loadingEl.style.display = "block";
  resultsEl.style.display = "none";

  try {
    const res = await fetch(`http://localhost:8000/agent/chat/${sessionId}`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    loadingEl.style.display = "none";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    transcriptText.textContent = data.transcript;
    assistantText.textContent = data.assistant_text;
    audioPlayer.src = `${API_BASE_URL}/files/${data.audio_file}`;
    audioPlayer.play().catch(() => { });
    resultsEl.style.display = "block";

    appendMessage("user", data.transcript);
    appendMessage("assistant", data.assistant_text);
    chatHistoryEl.style.display = "block";
  } catch (err) {
    loadingEl.style.display = "none";
    alert("Request failed: " + err);
  }
}

function appendMessage(role, text) {
  const messageDiv = document.createElement("div");
  messageDiv.style.marginBottom = "10px";

  if (role === "user") {
    messageDiv.innerHTML = `<strong style="color:#ffd700;">You:</strong> ${escapeHtml(text)}`;
  } else {
    messageDiv.innerHTML = `<strong style="color:#90ee90;">Assistant:</strong> ${escapeHtml(text)}`;
  }

  chatMessagesEl.appendChild(messageDiv);
  chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
