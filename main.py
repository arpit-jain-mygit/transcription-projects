import os
import json
import tempfile
import datetime
import smtplib
from email.message import EmailMessage

from flask import Flask, request
from google.cloud import storage
from google import genai

# ==========================
# CONFIG
# ==========================
INPUT_BUCKET = "jain-audio-input"
OUTPUT_BUCKET = "jain-audio-output"
MODEL_NAME = "gemini-2.5-flash"

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]

# ==========================
# CLIENTS
# ==========================
genai_client = genai.Client(api_key=GEMINI_API_KEY)
storage_client = storage.Client()

app = Flask(__name__)

# ==========================
# PROMPT
# ==========================
AUDIO_PROMPT = """<YOUR SAME AUDIO PROMPT>"""

# ==========================
# EMAIL
# ==========================
def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
        server.send_message(msg)

# ==========================
# TRANSCRIPTION
# ==========================
def transcribe(bucket_name, blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        blob.download_to_filename(f.name)

        uploaded = genai_client.files.upload(
            file=open(f.name, "rb"),
            config={"mime_type": "audio/mpeg"}
        )

        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded, AUDIO_PROMPT],
            config={"temperature": 0.1}
        )

        return response.text or ""

# ==========================
# SAVE OUTPUT
# ==========================
def save_output(text, original_name):
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base = original_name.rsplit(".", 1)[0]
    out_name = f"{base}_{ts}.txt"

    out_bucket = storage_client.bucket(OUTPUT_BUCKET)
    out_blob = out_bucket.blob(out_name)
    out_blob.upload_from_string(
        text,
        content_type="text/plain; charset=utf-8"
    )

    return out_name

# ==========================
# EVENTARC ENDPOINT
# ==========================
@app.route("/", methods=["POST"])
def receive_event():
    envelope = request.get_json()
    print("RAW EVENT:", envelope, flush=True)

    if not envelope:
        return "No event", 400

    # --------
    # Handle BOTH payload shapes:
    # 1) Raw GCS JSON (current)
    # 2) CloudEvents (data field)
    # --------
    bucket = envelope.get("bucket")
    name = envelope.get("name")

    if not bucket or not name:
        data = envelope.get("data", {})
        bucket = data.get("bucket")
        name = data.get("name")

    if not bucket or not name:
        print("Missing bucket or name after fallback", flush=True)
        return "Ignored", 200

    if bucket != INPUT_BUCKET or not name.lower().endswith(".mp3"):
        print(f"Ignored file: {bucket}/{name}", flush=True)
        return "Ignored", 200

    try:
        print(f"Processing {name}", flush=True)

        text = transcribe(bucket, name)
        out_file = save_output(text, name)

        send_email(
            subject="Transcription Completed",
            body=f"""
Input: {name}
Output: {out_file}
Bucket: {OUTPUT_BUCKET}
Status: SUCCESS
"""
        )

        print("Done", flush=True)
        return "OK", 200

    except Exception as e:
        print("ERROR:", str(e), flush=True)
        send_email(
            subject="Transcription FAILED",
            body=f"File: {name}\nError: {str(e)}"
        )
        return "Error", 500


# ==========================
# START SERVER (REQUIRED)
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
