import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, abort

app = Flask(__name__, static_folder="static", template_folder="templates")

# Chat storage folder (relative to project root)
CHAT_DIR = os.path.join(os.path.dirname(__file__), "chat")
os.makedirs(CHAT_DIR, exist_ok=True)

def safe_filename_for_timestamp(ts):
    # e.g. 20251023_153045_123456.json
    return ts.strftime("%Y%m%d_%H%M%S_%f") + ".json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def save_chat():
    """
    Expect JSON: { "user": "Name", "message": "Hello" }
    Saves each message as a separate JSON file in chat/ folder.
    Returns saved file info.
    """
    if not request.is_json:
        return jsonify({"error": "JSON expected"}), 400

    data = request.get_json()
    user = data.get("user", "anonymous")
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "message cannot be empty"}), 400

    timestamp = datetime.utcnow()
    filename = safe_filename_for_timestamp(timestamp)
    filepath = os.path.join(CHAT_DIR, filename)

    saved = {
        "user": str(user),
        "message": str(message),
        "timestamp_utc": timestamp.isoformat() + "Z"
    }

    # Write file (one file per message to avoid complex locking)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(saved, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok", "file": filename, "saved": saved}), 201

@app.route("/api/chat/list", methods=["GET"])
def list_chats():
    """
    Return list of messages sorted by filename (which follows timestamp order).
    """
    files = sorted([f for f in os.listdir(CHAT_DIR) if f.endswith(".json")])
    msgs = []
    for fname in files:
        try:
            with open(os.path.join(CHAT_DIR, fname), "r", encoding="utf-8") as f:
                msgs.append(json.load(f))
        except Exception:
            # skip corrupted file
            continue
    return jsonify({"count": len(msgs), "messages": msgs})

# Optional: serve chat files (not recommended for public without auth)
@app.route("/chat_files/<path:filename>")
def serve_chat_file(filename):
    # Basic safety check: allow only .json from CHAT_DIR
    if ".." in filename or not filename.endswith(".json"):
        abort(404)
    return send_from_directory(CHAT_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)