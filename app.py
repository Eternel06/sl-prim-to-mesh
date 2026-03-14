from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from prim_to_dae import prims_to_dae
import io
import json
import os
import uuid

app = Flask(__name__)
CORS(app)

# temporary storage for generated files
files = {}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "SL Prim to Mesh converter is running!"
    })

@app.route("/convert", methods=["GET", "POST"])
def convert():
    try:
        # try GET parameter first
        raw = request.args.get("data")

        # try POST body
        if not raw:
            raw = request.get_data(as_text=True)

        # try form data
        if not raw:
            raw = request.form.get("data")

        if not raw:
            return jsonify({"error": "No data received"}), 400

        try:
            data = json.loads(raw)
        except Exception as e:
            return jsonify({"error": "Invalid JSON: " + str(e)}), 400

        prims = data.get("prims", [])
        if not prims:
            return jsonify({"error": "No prims found"}), 400

        dae_content = prims_to_dae(prims)
        if not dae_content:
            return jsonify({"error": "DAE generation failed"}), 500

        # store file with unique id
        file_id = str(uuid.uuid4())
        files[file_id] = dae_content

        # return download URL as plain text
        base_url = request.host_url.rstrip("/")
        download_url = base_url + "/download/" + file_id
        return download_url, 200, {"Content-Type": "text/plain"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
