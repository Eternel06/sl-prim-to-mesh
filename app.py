from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from prim_to_dae import prims_to_dae
import io
import json
import os
import uuid

app = Flask(__name__)
CORS(app)

# storage for files and chunks
files = {}
sessions = {}

@app.route("/", methods=["GET"])
def home():
    return "SL Prim to Mesh converter is running!", 200, {"Content-Type": "text/plain"}

@app.route("/start", methods=["GET"])
def start():
    # create a new session
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    return session_id, 200, {"Content-Type": "text/plain"}

@app.route("/chunk", methods=["GET"])
def chunk():
    try:
        session_id = request.args.get("sid")
        raw = request.args.get("data")
        if not session_id or session_id not in sessions:
            return "Invalid session", 400, {"Content-Type": "text/plain"}
        if not raw:
            return "No data", 400, {"Content-Type": "text/plain"}
        prims = json.loads(raw)
        sessions[session_id].extend(prims)
        return "OK", 200, {"Content-Type": "text/plain"}
    except Exception as e:
        return "Error: " + str(e), 500, {"Content-Type": "text/plain"}

@app.route("/generate", methods=["GET"])
def generate():
    try:
        session_id = request.args.get("sid")
        if not session_id or session_id not in sessions:
            return "Invalid session", 400, {"Content-Type": "text/plain"}
        prims = sessions[session_id]
        if not prims:
            return "No prims found", 400, {"Content-Type": "text/plain"}
        dae_content = prims_to_dae(prims)
        if not dae_content:
            return "DAE generation failed", 500, {"Content-Type": "text/plain"}
        file_id = str(uuid.uuid4())
        files[file_id] = dae_content
        del sessions[session_id]
        base_url = request.host_url.rstrip("/")
        download_url = base_url + "/download/" + file_id
        return download_url, 200, {"Content-Type": "text/plain"}
    except Exception as e:
        return "Error: " + str(e), 500, {"Content-Type": "text/plain"}

@app.route("/download/<file_id>", methods=["GET"])
def download(file_id):
    if file_id not in files:
        return "File not found", 404
    dae_content = files[file_id]
    dae_bytes = io.BytesIO(dae_content.encode("utf-8"))
    dae_bytes.seek(0)
    return send_file(
        dae_bytes,
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name="prim_mesh.dae"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
