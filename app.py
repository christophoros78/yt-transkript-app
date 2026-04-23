from flask import Flask, request, render_template_string, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Transkrypt</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 40px auto; }
        textarea { width: 100%; height: 300px; }
        button { padding: 10px; margin-top: 10px; cursor: pointer; }
    </style>
</head>
<body>

<h2>YouTube → Transkrypt</h2>

<input id="url" style="width:100%" placeholder="Wklej link YouTube">
<br><br>
<button onclick="getTranscript()">Pobierz</button>

<h3>Transkrypt:</h3>
<textarea id="output"></textarea>
<br>

<button onclick="copyText()">📋 Kopiuj jednym kliknięciem</button>

<script>
async function getTranscript() {
    const url = document.getElementById("url").value;

    const res = await fetch("/api", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url})
    });

    const data = await res.json();
    document.getElementById("output").value = data.text;
}

function copyText() {
    const text = document.getElementById("output");
    text.select();
    document.execCommand("copy");
    alert("Skopiowano!");
}
</script>

</body>
</html>
"""

def get_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api", methods=["POST"])
def api():
    data = request.get_json()
    url = data.get("url")

    video_id = get_video_id(url)

    if not video_id:
        return jsonify({"text": "Nieprawidłowy link"})

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        text = " ".join([t.text for t in transcript])
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"text": f"Błąd: {e}"})

if __name__ == "__main__":
    app.run()